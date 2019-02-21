# Copyright (C) 2018 British Broadcasting Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from TestHelper import do_request
from GenericTest import NMOSTestException
from is08.testConfig import globalConfig


class Call:

    def __init__(self, url, string=False):
        self.string = string
        self.url = url
        self.expectedCode = 200
        self.test = globalConfig.test
        self._responseObject = None
        self._method = None
        self.responseSchema = None

    def _makeRequest(self):
        self._responseObject = do_request(self.method, self.url, self.data)
        self._checkForErrors()
        self._checkStatusCode()
        self._getJSON()

    def get(self):
        return self._genericRequestProcess("get")

    def post(self, data):
        return self._genericRequestProcess("post", data)

    def delete(self):
        return self._genericRequestProcess("delete")

    def _genericRequestProcess(self, method, data=None):
        (self._callSucceeded, self._responseObject) = do_request(method, self.url, data)
        return self._processResponseObject()

    def _processResponseObject(self):
        self._checkForErrors()
        self._checkStatusCode()
        self._checkResponseSchema()
        return self._getJSON()

    def _checkForErrors(self):
        if not self._callSucceeded:
            raise NMOSTestException(self.test.FAIL(self._responseObject))

    def _checkStatusCode(self):
        if self.expectedCode is not None:
            statusCode = self._responseObject.status_code

            if statusCode != self.expectedCode:
                msg = (self.test.FAIL("Un-expected response code {} from url {}, expected"
                       " {}".format(statusCode, self.url, self.expectedCode)))
                raise NMOSTestException(self.test.FAIL(msg))

    def _checkResponseSchema(self):
        if self.responseSchema is not None:
            globalConfig.testSuite.check_response(
                globalConfig.apiKey,
                self.responseSchema,
                self._method,
                self._responseObject
            )

    def _getJSON(self):
        if self.string:
            return self._responseObject.text
        else:
            try:
                response = self._responseObject.json()
            except ValueError:
                raise NMOSTestException(self.test.FAIL("Invalid JSON received from {}".format(self.url)))
            return response