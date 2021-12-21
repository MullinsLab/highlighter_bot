import re, os, sys, wget, glob, time
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from robobrowser import RoboBrowser

browser = RoboBrowser(history=True, parser='lxml')
url = "https://www.hiv.lanl.gov/content/sequence/HIGHLIGHT/highlighter_top.html?choice=mismatches"
download_url = "https://www.hiv.lanl.gov"
#download_referer = "https://www.hiv.lanl.gov/cgi-bin/HIGHLIGHT/highlighter.cgi"
browser.open(url)
form = browser.get_form(action=re.compile(r'highlighter.cgi'))

path = os.getcwd()
files = glob.glob(path + '/*.fasta')
filenum = 0
full_time = time.time()

for file in files:
    filenum += 1
    job_time = time.time()

    alignmentFilePath = file
    cur_seq_name = os.path.splitext(file)[0]
    treeFilePath = cur_seq_name+'.phy_phyml_tree.txt_newick.tre'
    #print('alignmentFilePath: ' + alignmentFilePath)
    #print('treeFilePath: ' + treeFilePath)
    #print('cur_seq_name: ' + cur_seq_name)
    save_png = os.path.join(path, cur_seq_name + '_highlighter.png')
    save_data = os.path.join(path, cur_seq_name + '_highlighter.txt')

    if not os.path.isfile(alignmentFilePath):
        sys.exit("File not found: " + alignmentFilePath)

    if not os.path.isfile(treeFilePath):
        sys.exit("File not found: " + treeFilePath)

    if os.path.isfile(save_png):
        print('Skipping {}, PNG already exists'.format(cur_seq_name))
        continue

    if os.path.isfile(save_data):
        print('Odd, data file .txt exists but not PNG for {}. Proceeding anyway.'.format(cur_seq_name))

    form["alignmentFile"].value = open(alignmentFilePath, 'r')
    form["uploadTree"].value = open(treeFilePath, 'r')
    form["choice"].value = "mismatches"
    form["sort"].value = "tree"
    form["treeType"].value = "upload"
    form["tw_multiplier"].value = "7"
    form["apobec"].value = "yes"
    form["submit"].value = ""  ### There are 2 input type="submit", we need the second one

    browser.session.headers['Referer'] = url

    print('Submitting file {}, {}'.format(filenum,cur_seq_name))
    browser.submit_form(form)

    # save the PNG and TXT results
    anchors = browser.find_all('a', {'href': True})

    for anchor in anchors:
        if "highlighter.png" in anchor['href'] and "[View large]" in anchor.contents[0]:
            image = download_url + anchor['href']
            data = download_url + anchor['href'][0:anchor['href'].index("png")] + "txt"

    wget.download(image, save_png)
    wget.download(data, save_data)

    jt = int(time.time() - job_time)
    print('Took {} seconds to downloaded PNG and TXT from highlighter for file: {}'.format(jt, cur_seq_name))
    
    # please be courteous to the server's resources and do not reduce the sleep time between jobs below 60 seconds
    time.sleep(90)

ft = int(time.time() - full_time)
print('All done! Completed in {} seconds. Exiting.'.format(ft))
