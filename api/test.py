from datetime import datetime

from api.faceme_api import FaceMeSdkApi


def main():
    image_path = '../data/test1.jpg'
    image2_path = '../data/test2.jpg'
    face1_template_path = '../data/test1.ft'
    face2_template_path = '../data/test1.ft'

    api = FaceMeSdkApi()

    # call api methods
    api.health_check()
    api.engine_status()

    result = api.enrollment(image_id='test_{}'.format(datetime.now().timestamp()), image_path=image_path,
                            features={'showDetail': True})
    image_id = result['imageMetadata']['imageID']
    print('image_id: {}'.format(image_id))

    api.compare_image_similarity(image1_path=image_path, image2_path=image2_path,
                                 features={'qualityCheck': False, 'showDetail': True})

    api.compare_image_similarity_by_id(image1_path=image_path,
                                       search_criteria={'imageID': image_id},
                                       features={'qualityCheck': True, 'showDetail': True})

    face_info = {'face1FeatureType': 3, 'face1FeatureSubType': 0, 'face1ByteOrder': 'big', 'face2FeatureType': 3,
                 'face2FeatureSubType': 0, 'face2ByteOrder': 'big'}
    api.face_template_comparison(face1_template_path, face2_template_path, face_info)

    api.search_similar_faces(image_path, features={'qualityCheck': False, 'showDetail': True},
                             search_criteria={'returnCount': 3})

    api.face_quality_check(image1_path=image_path, features={'qualityCheck': True})

    api.delete_enrollment(image_id=result['imageMetadata']['imageID'])

    detail = {"precisionLevel": "standard", "cameraInfo": "Vimicro USB2.0 PC Camera (0ac8:3410)",  # "still": 6,
              "enable2Stage": False,
              "status": [0.648, 0.593, 0.552, 0.534, 0.496, 0.536, 0.539, 0.565, 0.6136, 0.6245, 0.625, 0.6070, 0.6367,
                         0.648, 0.645],
              }
    api.check_spoofing_attack([image_path, image2_path], detail)

    detail = {"precisionLevel": "standard", "cameraInfo": "Vimicro USB2.0 PC Camera (0ac8:3410)", "dir": "left",
              "previous": 0.52726555}
    api.check_spoofing_attack_second_stage([image_path, image2_path], detail)


if __name__ == '__main__':
    main()
