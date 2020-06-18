import json
from pathlib import Path

import requests
from requests_toolbelt.multipart import decoder

"""
FaceMe SDK HTTP API - Python bridge to invoke API
For more detailed API input/output parameters go through pdf "FaceMe SDK HTTP API Document" 
"""


class FaceMeSdkApi:

    def __init__(self, api_endpoint=None, user=None, access_code=None):
        """
        Initialize attributes
        :param access_code: token for API
        :param user: default to cyberlink
        :param api_endpoint: api end point. default to localhost:8080
        """
        print('Initializing FaceMe sdk api python interface')
        if not access_code:
            # default access code
            self.access_code = 'Y3liZXJsaW5rOjM3NzMzOWFhMTA3YWU1OGFiZThlM2M3ZmQzMDIxOGI2'
        else:
            self.access_code = access_code

        if not user:
            # set user as cyberlink by default
            self.user = 'cyberlink'
        else:
            self.user = user

        if not api_endpoint:
            # default to localhost
            self.api_endpoint = 'http://localhost:8080/mp/api/v1.0'
        else:
            self.api_endpoint = api_endpoint

    def _get_api_url(self, api_path):
        """
        format api endpoint url
        :param api_path:
        :return: url: API endpoint url
        """
        url = '{}{}'.format(self.api_endpoint, api_path)
        print('Api end point: {}'.format(url))
        return url

    def _get_http_auth_header(self):
        """
        HTTP Headers
        :return: http_headers
        """
        http_headers = {
            'Authorization': 'Basic {}'.format(self.access_code)
        }
        return http_headers

    @staticmethod
    def _result_from_response(resp):
        """
        extract json data from http response
        :param resp:
        :return: Json data
        """
        resp.raise_for_status()
        json_output = resp.json()
        print(json_output)
        return json_output

    def health_check(self):
        """
        1.1. Health Monitor
        Health check API
        Health check API for load balancer to monitor CyberLink APP server status
        :return: None
        """
        print('Performing health check')

        resp = requests.get(url=self._get_api_url('/health'))
        resp.raise_for_status()

        output = resp.text
        assert output == 'FACEME IS OK', 'Service Unavailable'
        print('Server is healthy: {}'.format(output))

    def engine_status(self):
        """
        Check Engine setup status. ENGINE INFO
        :return: json string
        """
        print('Performing setup status check')

        resp = requests.post(url=self._get_api_url('/service/faceme/status'), headers=self._get_http_auth_header(),
                             data={})

        return self._result_from_response(resp)

    def enrollment(self, image_id, image_path, features={'showDetail': True}):
        """
        1.2. Enrollment
        Insert a new face
        This method accepts images with following characteristics:
            Format: PNG/BMP/JPG/JPEG
        :param image_id:
        :param image_path:
        :param features: features JSON
        :return: Json response
        """
        print('Enrolling image_id: {}'.format(image_id))
        files = [
            ('image', (Path(image_path).name, open(image_path, 'rb'), 'image/jpeg')),
            ('imageMetadata', (None, json.dumps({'imageID': image_id}), 'application/json')),
            ('features', (None, json.dumps(features), 'application/json'))
        ]

        resp = requests.post(url=self._get_api_url('/records'), headers=self._get_http_auth_header(), files=files)

        return self._result_from_response(resp)

    def delete_enrollment(self, image_id):
        """
        1.3. Delete record
        Remove a face record
        delete enrollment record
        :param image_id: image_id to be deleted
        :return: json response
        """
        print('Deleting previously enrolled image_id: {}'.format(image_id))

        _headers = {'Content-Type': 'application/json'}
        _headers.update(self._get_http_auth_header())

        resp = requests.post(url=self._get_api_url('/withdraw'), headers=_headers,
                             data=json.dumps({'imageID': image_id}))

        return self._result_from_response(resp)

    def compare_image_similarity(self, image1_path, image2_path, features={'qualityCheck': False, 'showDetail': True}):
        """
        1.4. 1-to-1 Comparison
        Compare similarity between two face images
        :param image1_path:
        :param image2_path:
        :param features: features JSON
        :return: json response
        """
        print('Comparing images for similarity')
        files = [
            ('image1', (Path(image1_path).name, open(image1_path, 'rb'), 'image/jpeg')),
            ('image2', (Path(image2_path).name, open(image2_path, 'rb'), 'image/jpeg')),
            ('features', (None, json.dumps(features), 'application/json'))
        ]

        resp = requests.post(url=self._get_api_url('/comparison'), headers=self._get_http_auth_header(), files=files)

        return self._result_from_response(resp)

    def face_template_comparison(self, face1_template_path, face2_template_path, faces_info):
        """
        1.5. 1-to-1 Face Templates Comparison
        Compare similarity between two faces according to their face templates.
        The two faces for comparing should use the same feature type.
        If the feature type is different, the API will respond error because it’s meaningless.
        :param face1_template_path:
        :param face2_template_path:
        :param faces_info:
        :return: json response
        """
        print('Comparing images for similarity using face templates')
        files = [
            ('face1Template',
             (Path(face1_template_path).name, open(face1_template_path, 'rb'), 'application/octet-stream')),
            ('face2Template',
             (Path(face2_template_path).name, open(face2_template_path, 'rb'), 'application/octet-stream')),
            ('facesInfo', (None, json.dumps(faces_info), 'application/json'))
        ]

        resp = requests.post(url=self._get_api_url('/face/compare11'), headers=self._get_http_auth_header(),
                             files=files)

        return self._result_from_response(resp)

    def search_similar_faces(self, image1_path, features, search_criteria):
        """
        1.6. 1-to-N Comparison
        Search similar faces from enrolled face dataset
        :param image1_path:
        :param features:
        :param search_criteria:
        :return: json response
        """
        print('Comparing images for similarity')
        files = [
            ('image1', (Path(image1_path).name, open(image1_path, 'rb'), 'image/jpeg')),
            ('features', (None, json.dumps(features), 'application/json')),
            ('searchCriteria', (None, json.dumps(search_criteria), 'application/json'))
        ]

        resp = requests.post(url=self._get_api_url('/comparison'), headers=self._get_http_auth_header(), files=files)

        return self._result_from_response(resp)

    def compare_image_similarity_by_id(self, image1_path, search_criteria, features):
        """
        1.7. 1-to-1 ID Comparison
        Compare similarity between input image and one specific image ID
        :param image1_path:
        :param search_criteria: JSON
        :param features: features JSON
        :return: json response
        """
        print('Compare similarity between input image and one specific image ID')
        files = [
            ('features', (None, json.dumps(features), 'application/json')),
            ('searchCriteria', (None, json.dumps(search_criteria), 'application/json')),
            ('image1', (Path(image1_path).name, open(image1_path, 'rb'), 'image/jpeg')),

        ]

        resp = requests.post(url=self._get_api_url('/comparison'), headers=self._get_http_auth_header(), files=files)

        return self._result_from_response(resp)

    def check_spoofing_attack(self, images, detail):
        """
        1.8. Anti-Spoofing without Interactions
        Verify if there is a spoofing attack in input images.
        For how to integrate the anti-spoofing API, please leverage the Web Component and the Web Sample code.
        :param images: array of images
        :param detail: {"precisionLevel":"standard","cameraInfo":"Vimicro USB2.0 PC Camera (0ac8:3410)",
                "status":[0.648,0.593,0.552,0.534,0.496,0.536,0.539,0.565,0.6136,0.6245, 0.625,0.6070,0.6367,0.648,0.645],
                "still":6,"enable2Stage":false}
        :return: Json output
        """

        print('Verify if there is a spoofing attack in input images')
        files = [
            ('detail', (None, json.dumps(detail), 'application/json')),
        ]
        for index, image in enumerate(images):
            files.append(('image{}'.format(index + 1), (Path(image).name, open(image, 'rb'), 'image/jpeg')))

        resp = requests.post(url=self._get_api_url('/spoofingcheck'), headers=self._get_http_auth_header(), files=files)

        resp.raise_for_status()

        # extract multi part result
        multipart_data = decoder.MultipartDecoder.from_response(resp)
        if multipart_data.parts:
            part = multipart_data.parts[0]
            result = json.loads(part.content)
            print(result)
            return result

        return None

    def check_spoofing_attack_second_stage(self, images, detail):
        """
        1.9. Anti-Spoofing with Interactions
        Second stage that to verify if there is a spoofing attack in input images.
        For how to integrate the anti-spoofing API, please leverage the Web Component and the Web Sample code.
        :param images: array of images
        :param detail: {"precisionLevel":"standard","cameraInfo":"Vimicro USB2.0 PC Camera (0ac8:3410)",
                        "dir":"left","previous":0.52726555}
        :return: Json output
        """

        print('Verify if there is a spoofing attack in input images')
        files = [
            ('detail', (None, json.dumps(detail), 'application/json')),
        ]
        for index, image in enumerate(images):
            files.append(('image{}'.format(index + 1), (Path(image).name, open(image, 'rb'), 'image/jpeg')))

        resp = requests.post(url=self._get_api_url('/spoofingcheckV2'), headers=self._get_http_auth_header(),
                             files=files)
        resp.raise_for_status()

        # extract multi part result
        multipart_data = decoder.MultipartDecoder.from_response(resp)
        if multipart_data.parts:
            part = multipart_data.parts[0]
            result = json.loads(part.content)
            print(result)
            return result

        return None

    def face_quality_check(self, image1_path, features):
        """
        1.11. Face image quality check
        Check quality of face image
        :param image1_path:
        :param features:
        :return: json response
        """
        print('Comparing images for similarity')
        files = [
            ('image', (Path(image1_path).name, open(image1_path, 'rb'), 'image/jpeg')),
            ('features', (None, json.dumps(features), 'application/json')),
        ]

        resp = requests.post(url=self._get_api_url('/faceimagequalitycheck'), headers=self._get_http_auth_header(),
                             files=files)

        return self._result_from_response(resp)
