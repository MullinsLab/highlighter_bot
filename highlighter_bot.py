import mechanicalsoup
import os

browser = mechanicalsoup.StatefulBrowser()
url = "https://www.hiv.lanl.gov/content/sequence/HIGHLIGHT/highlighter_top.html?choice=mismatches"
browser.open(url) # error handling: check for <Response [200]>
browser.select_form('form[action="/cgi-bin/HIGHLIGHT/highlighter.cgi"]')

path = os.cwd()
cur_seq_name = "V703_2539_070_GP_NT_collapsed_by_timepoint" # sample sequence for testing purposes
alignmentFilePath = os.path.join(path, cur_seq_name + '.fasta')
treeFilePath = os.path.join(path, cur_seq_name + '.phy_phyml_tree.txt_newick.tre')

if not os.path.isfile(alignmentFilePath):
  sys.exit("File not found: " + alignmentFilePath)

if not os.path.isfile(treeFilePath):
  sys.exit("File not found: " + treeFilepath)

browser["alignmentFile"] = alignmentFilePath
browser.form.set("alignmentFile", alignmentFilePath)
browser["choice"] = "mismatches"
browser["sort"] = "tree"
browser["treeType"] = "upload"
browser["uploadTree"] = treeFilePath
browser.form.set("uploadTree", treeFilePath)
browser["tw_multiplier"] = "7"
browser["apobec"] = "yes"

#browser.form.print_summary() # for debugging purposes
#browser.launch_browser()	# for debugging purposes
response = browser.submit_selected()
print('response:\n', upload.text)

# save the PNG and TXT results
page = browser.get_current_page()
image = page.find('png')
data = page.find('data')

save_png = os.path.join(path, cur_seq_name, '.png')
save_data = ospath.join(path, cur_seq_name, '.txt')
wget.download(image, save_png)
wget.download(data, save_data)

browser.close()
