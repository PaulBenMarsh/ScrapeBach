
def main():

    import requests
    from bs4 import BeautifulSoup
    from pathlib import Path

    base_url = "http://www.jsbach.net/midi"

    url = f"{base_url}/index.html"

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for a in soup.select("tr a[href^=\"midi\"]"):

        url = f"{base_url}/{a['href']}"
        response = requests.get(url)
        try:
            response.raise_for_status()
        except requests.HTTPError:
            print(f"Skipping '{url}'...")
            continue

        broth = BeautifulSoup(response.text, "html.parser")

        path = Path(f"./midi/{a.text.strip()}")
        path.mkdir(parents=True, exist_ok=True)

        for a in broth.select("tr td font a"):
            href = a["href"]
            if not any(href.endswith(extension) for extension in (".mid", ".zip", ".txt")):
                continue
            resource_url = f"{base_url}/{href}"
            response = requests.get(resource_url, stream=True)
            try:
                response.raise_for_status()
            except requests.HTTPError:
                print(f"Skipping resource {resource_url}...")
                continue

            file_path = path/Path(href).parts[-1]
            with file_path.open("wb") as file:
                for chunk_n, chunk in enumerate(response.iter_content(chunk_size=8192)):
                    if chunk:
                        file.write(chunk)
                file.flush()
            print(f"Downloaded {file_path}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
