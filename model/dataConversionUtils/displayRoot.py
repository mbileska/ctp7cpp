import uproot

def display_root_contents(root_file_path):
    # Open the ROOT file using uproot
    with uproot.open(root_file_path) as file:
        print(f"Contents of the ROOT file: {root_file_path}\n")

        # Iterate through each key in the ROOT file to identify trees
        for name, tree in file.items():
            if isinstance(tree, uproot.behaviors.TTree.TTree):
                print(f"Tree: {name}")

                # Correctly accessing branches within the tree
                branches = tree.keys()
                for branch_name in branches:
                    branch = tree[branch_name]
                    print(f"  Branch: {branch_name}")

                    # Access leaves under this branch
                    leaves = branch.typenames()
                    for leaf_name in leaves:
                        print(f"    Leaf: {leaf_name} (Type: {leaves[leaf_name]})")
                print()  # Add a newline for better separation between trees

if __name__ == "__main__":
    root_file_path = "l1TNtuple-ggHBB_11.root"  # Path to your ROOT file
    display_root_contents(root_file_path)
