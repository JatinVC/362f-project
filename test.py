import json, subprocess, time, unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import threading

SERVER = 'localhost:5000'

def ws_client(url, method, data=None):
    if data:
        data = json.dumps(data).encode("utf-8")
    headers = {"Content-type": "application/json; charset=UTF-8"} if data else {}

    req = Request(url=url, data=data, headers=headers, method=method)
    with urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result

def flatten_dict(dictionary):
    keys = []
    for key, value in dictionary.items():
        if type(value) is dict:
            keys.append(key)
            for internalKey in value.keys():
                keys.append(internalKey)
        else:
            keys.append(key)
    return keys

class TestServer(unittest.TestCase):
    # @classmethod
    # def setUpClass(cls):
    #     cls.server_proc = subprocess.Popen(['python', 'run.py'])
    #     time.sleep(0.5)

    # @classmethod
    # def tearDownClass(cls):
    #     cls.server_proc.terminate()
    

    # all the unit tests here
    def test_product_query(self):
        try:
            query_resp = ws_client(f"http://{SERVER}/products/1", 'GET')
            keys = ['success','exe_id','product','id','description','cost','quantity']
            self.assertCountEqual(keys, flatten_dict(query_resp))
        except HTTPError as e:
            self.assertEqual(400, e.code)
    

    def test_successful_product_purchase(self):
        data = {'quantity': 1,'credit_card':1234567891011123}
        query_resp = ws_client(f"http://{SERVER}/buy/1",'POST',data)
        self.assertTrue(query_resp['success'])
    

    def test_unsuccessful_product_purchase(self):
        query_resp_before = ws_client(f"http://{SERVER}/products/1", 'GET')
        try:
            data = {'quantity': 50,'credit_card':1234567891011123}
            query_resp = ws_client(f"http://{SERVER}/buy/1", 'POST', data)
            self.assertTrue(query_resp['success'])
        except HTTPError as e:
            self.assertEqual(404, e.code)
        # check if quantity has not reduced
        query_resp_after = ws_client(f"http://{SERVER}/products/1", 'GET')
        self.assertEqual(query_resp_after['product']['quantity'], query_resp_before['product']['quantity'])


    def test_replenish_stock(self):
        query_resp_before = ws_client(f"http://{SERVER}/products/1", 'GET')
        query_resp = ws_client(f"http://{SERVER}/stock/1/5", 'PUT')
        query_resp_after = ws_client(f"http://{SERVER}/products/1", 'GET')
        self.assertEqual(query_resp_before['product']['quantity']+5, query_resp_after['product']['quantity'])


    def test_unsuccessful_product_query(self):
        try:
            query_resp = ws_client(f"http://{SERVER}/products/100", 'GET')
        except HTTPError as e:
            self.assertEqual(404, e.code)
    

    def test_invalid_data(self):
        query_resp_before = ws_client(f"http://{SERVER}/products/1", 'GET')
        try:
            data = {'quantity': 50,'credit_card':12345}
            query_resp = ws_client(f"http://{SERVER}/buy/1", 'POST', data)
            self.assertTrue(query_resp['success'])
        except HTTPError as e:
            self.assertEqual(400, e.code)
        # check if quantity has not reduced
        query_resp_after = ws_client(f"http://{SERVER}/products/1", 'GET')
        self.assertEqual(query_resp_before['product']['quantity'], query_resp_before['product']['quantity'])

    # test multiple simultaneos requests
    def test_multiple_purchase_requests(self):

        query_resp_before = ws_client(f"http://{SERVER}/products/1", 'GET')

        def request_thread(thread_no):
            if thread_no == 1:
                # this is the first request
                data = {'quantity': 1,'credit_card':1234567891011123}
                query_resp = ws_client(f"http://{SERVER}/buy/1",'POST',data)
                self.assertTrue(query_resp['success'])
            else:
                # this is the second request
                try:
                    data = {'quantity': 50,'credit_card':1234567891011123}
                    query_resp = ws_client(f"http://{SERVER}/buy/1",'POST',data)
                    self.assertTrue(query_resp['success'])
                except HTTPError as e:
                    self.assertEqual(404, e.code)

        request_threads = []
        thread_no = 1
        t = threading.Thread(target=request_thread, args=[thread_no])
        request_threads.append(t)
        thread_no+=1
        t1 = threading.Thread(target=request_thread, args=[thread_no])
        request_threads.append(t1)

        for thread in request_threads:
            thread.start()

        query_resp_after = ws_client(f"http://{SERVER}/products/1", 'GET')
        self.assertEqual(query_resp_before['product']['quantity'] - 1, query_resp_after['product']['quantity'])

if __name__ == '__main__':
    unittest.main()