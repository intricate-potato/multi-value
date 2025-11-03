__version__ = "0.1"
__organization__ = "Social And Language Technology Lab"
import nltk
import spacy
from spacy.util import is_package

# Attempt to ensure required resources are available, but avoid forcing
# an unconditional download on import. If the package isn't installed,
# try to download it once and otherwise print a helpful message so the
# user can install it manually (e.g. via downloads.sh or pip).
try:
	if not is_package("en_core_web_sm"):
		try:
			# defer import of download to only when needed
			from spacy.cli import download
			download("en_core_web_sm")
		except Exception as e:
			# don't raise here — just inform the user
			print(
				"Warning: could not auto-download en_core_web_sm."
				" Please install it manually (see SETUP_NOTES.md or run downloads.sh)."
			)
except Exception:
	# If spacy itself isn't importable or something else goes wrong,
	# skip automatic handling and let the later code surface the error.
	pass

nltk.download("cmudict")
nltk.download("wordnet")
