import os
from PIL import Image
import numpy as np
import cv2
import copy

from object_detection import config
from object_detection import functions

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
from object_detection.utils import ops as utils_ops

import tensorflow as tf

if config.to_download:
    functions.download_graph(config.model['download_base_url'], config.model['file'])

# Load model
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(config.model['path'], 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

label_map = label_map_util.load_labelmap(config.model['label'])
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=config.maximum_classes_to_detect,
                                                            use_display_name=True)
category_index = label_map_util.create_category_index(categories)

frames = 0
vidcap = 0
base_dir = ''
counter = 0

write_video_feed = ''

if config.is_image:
    base_dir = config.path['image_dir']
    all_images = os.listdir(base_dir)

else:
    video_path = config.path['video_dir']
    video_name = config.path['video_name']
    video_full = os.path.join(video_path, video_name)
    print(video_path)
    if not os.path.exists(config.path['output_video_dir']):
        os.makedirs(config.path['output_video_dir'])
    vidcap = cv2.VideoCapture(video_full)
    frames = functions.count_frames_manual(vidcap)
    print('total frmames', frames)
    all_images = range(frames)
    vidcap.release()
    vidcap = cv2.VideoCapture(video_full)
    frame_width = int(vidcap.get(3))
    frame_height = int(vidcap.get(4))
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    fps_int = int(round(fps))
    write_video_feed = cv2.VideoWriter(os.path.join(config.path['output_video_dir'], config.path['output_video_name']),
                                       cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                                       fps_int,
                                       (frame_width, frame_height))
with detection_graph.as_default():
    with tf.Session() as sess:

        for each_image in all_images:

            if config.is_image:
                image_path = os.path.join(base_dir, each_image)
                image = Image.open(image_path)
                image_np = functions.load_image_into_numpy_array(image)
            else:
                rev, image_np = vidcap.read()
            # the array based representation of the image will be used later in order to prepare the
            # result image with boxes and labels on it.
            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image_np, axis=0)
            # Actual detection.

            ops = tf.get_default_graph().get_operations()
            all_tensor_names = {output.name for op in ops for output in op.outputs}
            tensor_dict = {}
            for key in [
                'num_detections', 'detection_boxes', 'detection_scores',
                'detection_classes', 'detection_masks'
            ]:
                tensor_name = key + ':0'
                if tensor_name in all_tensor_names:
                    tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
                        tensor_name)
            if 'detection_masks' in tensor_dict:
                # The following processing is only for single image
                detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
                detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
                # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
                detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
                detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
                detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                    detection_masks, detection_boxes, image_np.shape[0], image_np.shape[1])
                detection_masks_reframed = tf.cast(
                    tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                # Follow the convention by adding back the batch dimension
                tensor_dict['detection_masks'] = tf.expand_dims(
                    detection_masks_reframed, 0)
            image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

            # Run inference
            output_dict = sess.run(tensor_dict,
                                   feed_dict={image_tensor: np.expand_dims(image_np, 0)})

            # all outputs are float32 numpy arrays, so convert types as appropriate
            output_dict['num_detections'] = int(output_dict['num_detections'][0])
            output_dict['detection_classes'] = output_dict[
                'detection_classes'][0].astype(np.uint8)
            output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
            output_dict['detection_scores'] = output_dict['detection_scores'][0]
            if 'detection_masks' in output_dict:
                output_dict['detection_masks'] = output_dict['detection_masks'][0]

            image_np_copy = copy.deepcopy(image_np)
            if config.show_labels:
                vis_util.visualize_boxes_and_labels_on_image_array(
                    image_np_copy,
                    output_dict['detection_boxes'],
                    output_dict['detection_classes'],
                    output_dict['detection_scores'],
                    category_index,
                    instance_masks=output_dict.get('detection_masks'),
                    use_normalized_coordinates=True,
                    line_thickness=8)

            number = min(config.minimum_detection, output_dict['num_detections'])
            for i in range(number):
                class_name = category_index[output_dict['detection_classes'][i]]['name']
                if config.detect_all_categories == False and not class_name in config.categories:
                    continue

                # print(output_dict['detection_scores'][i])
                # cv2.imshow('test', cv2.resize(image_np, (800, 600)))
                # print(output_dict['detection_classes'][i])
                base_path = os.path.join(config.path['output_image_dir'], class_name)
                coord = output_dict['detection_boxes'][i]
                y1, x1, y2, x2 = coord[0], coord[1], coord[2], coord[3]
                y1 -= ((y2 - y1) * config.motor_person_offset_percent / 100)
                if y1 < 0:
                    y1 = 0
                y1 = int(y1 * image_np.shape[0])
                y2 = int(y2 * image_np.shape[0])
                x1 = int(x1 * image_np.shape[1])
                x2 = int(x2 * image_np.shape[1])

                cropped_img = image_np[y1:y2, x1:x2]
                if not os.path.exists(base_path):
                    os.makedirs(base_path)
                if config.save_by_class:
                    cv2.imwrite(os.path.join(base_path, str(counter * config.minimum_detection + i) + '.jpg'),
                                cropped_img)
            # os.system('eog name.png &')
            # print(output_dict['detection_masks'])
            # print('done')
            if config.to_show:
                cv2.imshow('test', cv2.resize(image_np_copy, (800, 600)))
            if config.to_save:
                if not os.path.exists(config.path['output_image_dir']):
                    os.makedirs(config.path['output_image_dir'])

                cv2.imwrite(os.path.join(config.path['output_image_dir'], str(counter) + '.jpg'), image_np_copy)
            counter += 1
            if config.generate_video:
                write_video_feed.write(image_np_copy)
                print('curr:', each_image)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
            # if cv2.waitKey(25) & 0xFF == ord('q'):
            #     break
cv2.destroyAllWindows()
if not config.is_image:
    write_video_feed.release()
