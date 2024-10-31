from pubmedFetcher import pubmedResults
from glyphilator import wordlists_from_folder,generateGlyphInput,constructBasicGlyphs


search_url = r"https://pubmed.ncbi.nlm.nih.gov/?term=monoclonal+antibody+allergy+asthma&size=200"
wordlists_path = r"C:\Users\aglis\Documents\Python_Projects\DaveArticleScraper\wordlists"

wordlists = wordlists_from_folder(wordlists_path)
print("Wordlists generated")
articleData = pubmedResults(search_url=search_url, num_results_requested=20)
print("articleData compiled")
allGlyphData = generateGlyphInput(articleData=articleData,wordlists=wordlists)
# print("glyphilator input complete")
# antzfile = constructBasicGlyphs(allGlyphData=allGlyphData)

# antzfile.to_csv(r"C:\Users\aglis\Documents\Python_Projects\DaveArticleScraper\output\antzfile.csv",index=False,encoding="utf-8")