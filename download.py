from pathlib import Path
import tarfile
import numpy as np
import shutil
from tqdm import tqdm
import arxiv
from utils.walker_download import color_latex_code, compile_pdf
from utils.tools import resize_image, load_json
import pdf2image
import time
import os


def download(url_file):
    # get paper ids
    paper_ids = []
    with open(url_file) as f:
        line = f.readline()
        while line:
            paper_ids.append(line.split("\t")[1])
            line = f.readline()
    temp = Path("temp")
    if temp.exists():
        shutil.rmtree(str(temp))
    train_pages = load_json(Path("Dataset/train/train_coco.json"))
    test_pages = load_json(Path("Dataset/test/test_coco.json"))
    train_img = Path("Dataset/train/img")
    test_img = Path("Dataset/test/img")
    train_img.mkdir(exist_ok=True)
    test_img.mkdir(exist_ok=True)
    with tqdm(paper_ids, postfix="download images") as pbar:
        for paper_id in pbar:
            pbar.set_description(f"download {paper_id}")
            paper_number = paper_id.split("/")[1].split("v")[0]
            # get train and val pages
            train_p = [page for page in train_pages if page.split('_')[0] == paper_number]
            test_p = [page for page in test_pages if page.split('_')[0] == paper_number]
            # continue if all images are already available
            if all([Path(train_img / page).exists() for page in train_p]) and all([Path(test_img / page).exists() for page in test_p]):
                continue
            # get paper
            start_time = time.time()
            paper = next(arxiv.Search(id_list=[paper_id]).results())
            # download paper
            temp.mkdir()
            if not paper.download_source(dirpath="temp", filename="temp.tar.gz"):
                print(f"Could not download {paper_id}")
            tar = tarfile.open(temp/"temp.tar.gz", "r:gz")
            tar.extractall(temp)
            tar.close()
            # rename largest tex file
            tex_files = sorted(temp.glob('*.tex'))
            if len(tex_files) > 0:
                tex_sizes = [tex_file.stat().st_size for tex_file in tex_files]
                os.rename(f"{tex_files[np.argmax(tex_sizes)]}", f"temp/{paper_number}.tex")
            else:
                with_out_suffix = [f for f in sorted(temp.glob("*")) if f.name.split(".")[0] == f.name]
                with_out_suffix_sizes = [with_out_s.stat().st_size for with_out_s in with_out_suffix]
                os.rename(f"{with_out_suffix[np.argmax(with_out_suffix_sizes)]}", f"temp/{paper_number}.tex")
            data = Path(f"temp/{paper_number}.tex").read_text()
            modified_data = color_latex_code(data)
            modified_file = temp / ('vanilla_' + paper_number + '.tex')
            modified_file.write_text(modified_data)
            if not compile_pdf(temp):
                print(f"Could not create PDF of {paper_number}")
                continue
            images = Path("temp/images")
            if images.exists():
                shutil.rmtree(images)
            images.mkdir()
            if not pdf2image.convert_from_path(modified_file.with_suffix(".pdf"), output_folder=images, fmt="jpeg", dpi=300):
                print(f"Could not create images of {paper_number}")
                continue
            image_list = sorted(images.glob("*.jpg"))
            for page in train_p:
                page_number = int(page.split("page")[1].split(".")[0])
                resize_image(image_list[page_number], {'w': 1447, 'h': 2048}, str(train_img / page))
            for page in test_p:
                page_number = int(page.split("page")[1].split(".")[0])
                resize_image(image_list[page_number], {'w': 1447, 'h': 2048}, str(test_img / page))
            shutil.rmtree(str(temp))
            wait_time = start_time-time.time()+5
            if wait_time > 0:
                time.sleep(wait_time)


if __name__ == '__main__':
    download("urls.txt")
