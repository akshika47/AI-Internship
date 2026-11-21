import sys, nbformat
from nbclient import NotebookClient
nb = nbformat.read("agent_sdk_examples.ipynb", as_version=4)
c = NotebookClient(nb, timeout=900, kernel_name="python3", allow_errors=True,
                   resources={"metadata": {"path": "."}})
c.execute()
nbformat.write(nb, "agent_sdk_examples.ipynb")
bad = []
for i, cell in enumerate(nb.cells):
    for o in cell.get("outputs", []):
        if o.output_type == "error":
            bad.append((i, o.ename, o.evalue, "\n".join(o.traceback[-6:])))
for b in bad:
    print("=== CELL", b[0], b[1], b[2][:300]); print(b[3][-1500:])
print("FAILED CELLS:", [b[0] for b in bad] or "none")
