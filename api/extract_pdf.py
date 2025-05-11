from PyPDF2 import PdfReader
from io import BytesIO
from requests import get


def read_remote_pdf(url, max_tokens=1000):
    '''
    Reads a pdf file from a remote url
     - returns a dictionary of type, content, metadata
    '''
    try:
        r = get(url)
        if r.status_code != 200:
            raise Exception(f"Error: {r.status_code}")
        # read pdf
        file = BytesIO(r.content)
        reader = PdfReader(file)
        number_of_pages = len(reader.pages)
        metadata = reader.metadata
        text = ""
        for i in range(number_of_pages):
            page = reader.pages[i]
            page_text = page.extract_text()
            if page_text:
                text += page_text
            if len(text) > max_tokens:
                break
        text = text.strip()[:max_tokens]
        return {
            "type": "pdf",
            "content": text,
            "metadata": metadata,
        }

    except Exception as e:
        print(e)
    return None


if __name__ == "__main__":
    print(read_remote_pdf(
        "https://www.ijsr.net/archive/v10i6/SR21610225258.pdf"))
