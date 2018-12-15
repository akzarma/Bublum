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
    'image_dir': os.path.join('input', 'images', 'aks'),
    'video_dir': os.path.join('input', 'videos'),
    'video_name': 'final1.mp4',
    'output_image_dir': os.path.join('output', 'images', 'rc_test'),
    'output_video_dir': os.path.join('output', 'videos','final'),
    'output_image_name': 'my_test',
    'output_video_name': 'final2.avi',
}

is_image = True
generate_video = False
# Size, in inches, of the output images.
image_size = (12, 8)

to_show = False

to_save = True
save_by_class = True

minimum_detection = 30

detect_all_categories = True
show_labels = True

categories = ['car', 'motorcycle', 'airplane', 'bus', 'truck', 'traffic light', 'person']
# categories = ['motorcycle']

motor_person_offset_percent = 30
