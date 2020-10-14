import requests
import json

class ApiClient(object):
    def __init__(self,apiKey, apiUri='https://api.elasticemail.com/v2'):
        self.apiUri = apiUri
        self.apiKey = apiKey

    def request(self,method, url, data, attach=None):
        """
        This method is used to do any API call to https://api.elasticemail.com/v2 URL.
        This method is helpful to do API call to send data to elasticemail server and process the response.
        Request is considered to be successful when value of success key received in response is True.


        :param method: This parameter specifies method by which data is to be sent. Allowed methods are POST, PUT, GET.
        :param url: Data will be sent to given URL in this parameter.
        :param data: The data passed here is sent further. Data here is expected in json format.
        :param attach: File Attachment that needs to be sent are to be passed in this parameter,
            also note that file will be sent only when method is POST.
            To send attachment in mail, first attach the file by following steps
            1) msg = EmailMultiAlternatives(subject, text_content, from_email, to_list)
            2) file_obj = open(invoice_obj.pdf.path, 'rb')
            3) msg.attach("filename.pdf",file_obj.read(),mimetype="application/pdf")
            Attached file is then appeneded in the mail for sending
        :return: On successful processing of response this returns value of data key received in response.
        """
        print('Request with attahcment') if attach else print('Request without attachment')
        tmp_attach = []
        for attachment in attach:
            # Append attachment received with refernce name as attachments
            tmp_attach.append(('attachments', attachment))
        data['apikey'] = self.apiKey
        if method == 'POST':
            result = requests.post(self.apiUri + url, data = data, files = tmp_attach)
        elif method == 'PUT':
            result = requests.put(self.apiUri + url, data = data)
        elif method == 'GET':
            attach = ''
            for key in data:
                attach = attach + key + '=' + data[key] + '&' 
            url = url + '?' + attach[:-1]
            result = requests.get(self.apiUri + url)
        
        if result.status_code == 200:
            json_result = result.json()
        else:
            print(result.status_code)
            raise Exception(result.text)
        if json_result['success'] is False:
            print("Failed to send email.{0}".format(json_result['error']))
            raise Exception("Failed to send email.{0}".format(json_result['error']))
        print("Email sent.{0}".format(json_result['data']))
        return json_result['data']

    def send_email(self,email,isTransactional=True, attachment_file=[]):
        email_data = {
            'subject': email['subject'],
            'from': email['senderEmail'],
            'fromName': email['senderName'],
            'msgTo': email['to'],
            'isTransactional': isTransactional
        }
        if 'bodyText' in email and email['bodyText']:
            email_data['bodyText'] = email['bodyText']
        if 'bodyHtml' in email and email['bodyHtml']:
            email_data['bodyHtml'] = email['bodyHtml']
        if 'cc' in email and email['cc']:
            email_data['msgCC']  = ';'.join(email['cc'])
        if 'bcc' in email and email['bcc']:
            email_data['msgBcc'] = ';'.join(email['bcc'])

        return self.request('POST', '/email/send', email_data, attach=attachment_file)