import json
import unittest

from signalbot import Quote


class TestQuote(unittest.TestCase):
    # Test data using same values as TestMessage
    raw_quote_message = '{"envelope":{"source":"+490123456789","sourceNumber":"+490123456789","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1632576001632,"syncMessage":{"sentMessage":{"destination":"+490123456789","destinationNumber":"+490123456789","destinationUuid":"<uuid>","timestamp":1632576001632,"message":"Ping","expiresInSeconds":0,"viewOnce":false,"quote":{"id":1632576001632,"author":"+490123456789","authorNumber":"+490123456789","authorUuid":"<uuid>","text":"","attachments":[{"contentType":"image/jpeg","filename":"image.jpg","thumbnail":{"contentType":"image/png","filename":null,"id":"1qeCjjWOOo9Gxv8pfdCw.png","size":21035,"width":150,"height":150,"caption":null,"uploadTimestamp":1632576001632}}]}}}},"account":"+490123456789"}'  # noqa: E501
    raw_quote_text_message = '{"envelope":{"source":"+490123456789","sourceNumber":"+490123456789","sourceUuid":"<uuid>","sourceName":"<name>","sourceDevice":1,"timestamp":1632576001632,"syncMessage":{"sentMessage":{"destination":"+490123456789","destinationNumber":"+490123456789","destinationUuid":"<uuid>","timestamp":1632576001632,"message":"Ping","expiresInSeconds":0,"viewOnce":false,"quote":{"id":1632576001632,"author":"+490123456789","authorNumber":"+490123456789","authorUuid":"<uuid>","text":"Ping","attachments":[]}}}},"account":"+490123456789"}'  # noqa: E501

    def test_quote_with_attachment(self):
        quote_data = json.loads(self.raw_quote_message)["envelope"]["syncMessage"][
            "sentMessage"
        ]["quote"]
        quote = Quote.model_validate(quote_data)

        assert quote.id == 1632576001632  # noqa: PLR2004
        assert quote.author == "+490123456789"
        assert quote.author_number == "+490123456789"
        assert quote.author_uuid == "<uuid>"
        assert quote.text == ""
        assert len(quote.attachments) == 1
        assert quote.attachments[0]["contentType"] == "image/jpeg"
        assert quote.attachments[0]["filename"] == "image.jpg"

    def test_quote_with_text(self):
        quote_data = json.loads(self.raw_quote_text_message)["envelope"]["syncMessage"][
            "sentMessage"
        ]["quote"]
        quote = Quote.model_validate(quote_data)

        assert quote.id == 1632576001632  # noqa: PLR2004
        assert quote.author == "+490123456789"
        assert quote.author_number == "+490123456789"
        assert quote.author_uuid == "<uuid>"
        assert quote.text == "Ping"
        assert len(quote.attachments) == 0

    def test_quote_from_dict(self):
        quote_dict = {
            "id": 123,
            "author": "+490123456789",
            "authorNumber": "+490123456789",
            "authorUuid": "<uuid>",
            "text": "Test quote",
            "attachments": [],
        }
        quote = Quote.model_validate(quote_dict)

        assert quote.id == 123  # noqa: PLR2004
        assert quote.author == "+490123456789"
        assert quote.author_number == "+490123456789"
        assert quote.author_uuid == "<uuid>"
        assert quote.text == "Test quote"
        assert len(quote.attachments) == 0


if __name__ == "__main__":
    unittest.main()
