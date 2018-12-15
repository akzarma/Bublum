import os

model = {
    'name': 'rc_graph',
    'graph_name': 'frozen_inference_graph.pb',
    'download_base_url': 'http://download.tensorflow.org/models/object_detection/',
    'label': os.path.join('labels', 'rc.pbtxt')
}

model['file'] = model['name'] + '.tar.gz'
model['path'] = os.path.join('models', model['name'], model['graph_name'])

to_download = False

maximum_classes_to_detect = 90

path = {
    'image_dir': os.path.join('input', 'images', 'final', 'bus'),
    'video_dir': os.path.join('input', 'videos'),
    'video_name': 'final4.mp4',
    'output_image_name': 'my_test',
    'output_video_name': 'final2.avi',
    'output_image_dir': os.path.join('output', 'images', 'rc'),
    'output_video_dir': os.path.join('output', 'videos'),
}

is_image = True
generate_video = False
# Size, in inches, of the output images.
image_size = (12, 8)

to_show = False

to_save = False
save_by_class = True

minimum_detection = 1

detect_all_categories = True
show_labels = True

categories = ['car', 'motorcycle', 'airplane', 'bus', 'truck', 'traffic light', 'person']
