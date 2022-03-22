import re, os, sys, wget, glob, time
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
import shutil
from robobrowser import RoboBrowser

browser = RoboBrowser(history=True, parser='lxml')
url = "https://www.hiv.lanl.gov/content/sequence/HIGHLIGHT/highlighter_top.html?choice=mismatches"
download_url = "https://www.hiv.lanl.gov"
#download_referer = "https://www.hiv.lanl.gov/cgi-bin/HIGHLIGHT/highlighter.cgi"
browser.open(url)
form = browser.get_form(action=re.compile(r'highlighter.cgi'))

path = os.getcwd()
files = glob.glob(path + '/*.fasta')
num_files = len(files)
filenum = 0
full_time = time.time()

for file in files:
    filenum += 1
    job_time = time.time()

    alignmentFilePath = file
    cur_seq_path = os.path.splitext(file)[0]
    cur_seq_name = os.path.basename(cur_seq_path)
    treeFilePath = cur_seq_path+'.phy_phyml_tree.txt_newick.tre'
    tmpAlignmentFilePath = os.path.join(path, '0_tmp.fasta')
    tmpTreeFilePath = os.path.join(path, '0_tmp_newick.tre')
    save_png = os.path.join(path, cur_seq_path + '_highlighter_untrimmed.png')
    save_data = os.path.join(path, cur_seq_path + '_highlighter.txt')
    save_rearr_fasta = os.path.join(path, cur_seq_path + '_highlighter.fasta')

    print("cur_seq_path: " + cur_seq_path)
    print("cur_seq_name: " + cur_seq_name)
    print("alignmentFilePath: " + alignmentFilePath)
    print("treeFilePath: " + treeFilePath)
    
    if not os.path.isfile(alignmentFilePath):
        sys.exit("File not found: " + alignmentFilePath)

    if not os.path.isfile(treeFilePath):
        sys.exit("File not found: " + treeFilePath)

    if os.path.isfile(save_png):
        print('Skipping {}, PNG already exists'.format(cur_seq_name))
        continue

    if os.path.isfile(save_data):
        print('Odd, data file .txt exists but not PNG for {}. Proceeding anyway.'.format(cur_seq_name))

    # if filenames are too long, use temporary shorter filenames
    if len(cur_seq_name) > 50:
        shutil.copyfile(alignmentFilePath, tmpAlignmentFilePath)
        shutil.copyfile(treeFilePath, tmpTreeFilePath)
        alignmentFilePath = tmpAlignmentFilePath
        treeFilePath = tmpTreeFilePath

    form["alignmentFile"].value = open(alignmentFilePath, 'r')
    form["uploadTree"].value = open(treeFilePath, 'r')
    form["choice"].value = "mismatches"
    form["sort"].value = "tree"
    form["treeType"].value = "upload"
    form["tw_multiplier"].value = "7"
    form["apobec"].value = "yes"
    form["submit"].value = ""  ### There are 2 input type="submit", we need the second one

    browser.session.headers['Referer'] = url

    print('Submitting file {}/{}, {}'.format(filenum,num_files,cur_seq_name))
    browser.submit_form(form)

    # save the PNG and TXT results
    anchors = browser.find_all('a', {'href': True})

    image = None
    data = None
    rearr_fasta = None

    for anchor in anchors:
        if "highlighter.png" in anchor['href'] and "[View large]" in anchor.contents[0]:
            image = download_url + anchor['href']
            data = download_url + anchor['href'][0:anchor['href'].index("png")] + "txt"
        elif "inseqs_rearr.fasta" in anchor['href']:
            rearr_fasta = download_url + anchor['href']

    if image == None:
        sys.exit("No image for: " + cur_seq_name)

    wget.download(image, save_png)
    wget.download(data, save_data)
    wget.download(rearr_fasta, save_rearr_fasta)

    # clean up temporary files
    if os.path.isfile(tmpAlignmentFilePath):
        os.remove(tmpAlignmentFilePath)
    if os.path.isfile(tmpTreeFilePath):
        os.remove(tmpTreeFilePath)

    jt = int(time.time() - job_time)
    print('Took {} seconds to downloaded PNG, TXT, and FASTA from Highlighter for file: {}'.format(jt, cur_seq_name))
    
    # please be courteous to the server's resources and do not reduce the sleep time between jobs below 60 seconds
    if filenum != num_files:
        time.sleep(90)

ft = int(time.time() - full_time)
print('All done! Completed in {} seconds. Exiting.'.format(ft))

# to trim PNGs for Phylobook, install ImageMagick and manually run:
#for f in *_untrimmed.png; do convert -crop +0+179 $f ${f%_untrimmed.png}.png; rm $f; done
