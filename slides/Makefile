LC = pdflatex
LCFLAGS = -interaction nonstopmode -output-directory $(OUTPUT)
OUTPUT = build

default: $(OUTPUT)/document.pdf

$(OUTPUT)/document.pdf: document.tex
	@mkdir -p $(OUTPUT)
	$(LC) $(LCFLAGS) $<

.PHONY: clean

clean:
	@rm -rf $(OUTPUT)
