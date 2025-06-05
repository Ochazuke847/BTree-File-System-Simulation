import numpy as np
from datetime import datetime
import os

# B-tree Node
class BTreeNode:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.child = []

# File Explorer (B-Tree implementation)
class FileExplorer:
    def __init__(self, t):
        self.root = BTreeNode(True)
        self.t = t

    # Insert a key
    def insert(self, k):                            # send in the tuple k (k[0] is the key, k[1] is the address that store the key)
        root = self.root                             # root node reference
        if len(root.keys) == (2 * self.t) - 1:      # in case of the root is full
            temp = BTreeNode()                      # create new node
            self.root = temp                        # Set the new node as new root
            temp.child.insert(0, root)              # set the old root node as the first child of the new root node
            self.split_child(temp, 0)               # split the old root node and insert its middle key into new root node
            self.insert_non_full(temp, k)           # insert k into the new tree
        else:
            self.insert_non_full(root, k)           # else just insert the k into the tree

    # Insert non full
    def insert_non_full(self, x, k):
        i = len(x.keys) - 1
        if x.leaf:                                  # in case of x is a leaf node
            if len(x.keys) < (2 * self.t) - 1:
                x.keys.append((None, None))
            while i >= 0 and (x.keys[i][0] is None or k[0] < x.keys[i][0]):
                x.keys[i + 1] = x.keys[i]
                i -= 1
            x.keys[i + 1] = k
        else:                                       # in case x is not a leaf node
            while i >= 0 and k[0] < x.keys[i][0]:
                i -= 1
            i += 1
            if len(x.child[i].keys) == (2 * self.t) - 1:
                self.split_child(x, i)
                if k[0] > x.keys[i][0]:
                    i += 1
            self.insert_non_full(x.child[i], k)

    # Split the child
    def split_child(self, x, i):
        t = self.t
        y = x.child[i]
        z = BTreeNode(y.leaf)
        x.child.insert(i + 1, z)
        x.keys.insert(i, y.keys[t - 1])
        z.keys = y.keys[t: (2 * t) - 1]
        y.keys = y.keys[0: t - 1]
        if not y.leaf:
            z.child = y.child[t: 2 * t]
            y.child = y.child[0: t]

    # Delete a node
    def delete(self, x, k_val):
        t = self.t
        i = 0
        while i < len(x.keys) and k_val > x.keys[i][0]:
            i += 1
        if x.leaf:
            if i < len(x.keys) and x.keys[i][0] == k_val:
                x.keys.pop(i)
                return
            else:
                return
        else:
            if i < len(x.keys) and x.keys[i][0] == k_val:
                return self.delete_internal_node(x, k_val, i)
            if len(x.child[i].keys) < t:
                self.fill(x, i)
            if i < len(x.child):
                self.delete(x.child[i], k_val)
            else:
                pass

    def delete_internal_node(self, x, k_val, i):
        t = self.t
        if len(x.child[i].keys) >= t:
            pred_key_tuple = self.get_predecessor(x, i)
            x.keys[i] = pred_key_tuple
            self.delete(x.child[i], pred_key_tuple[0])
        elif len(x.child[i + 1].keys) >= t:
            succ_key_tuple = self.get_successor(x, i)
            x.keys[i] = succ_key_tuple
            self.delete(x.child[i + 1], succ_key_tuple[0])
        else:
            self.merge(x, i)
            self.delete(x.child[i], k_val)

    def get_predecessor(self, x, i):
        cur = x.child[i]
        while not cur.leaf:
            cur = cur.child[len(cur.child) - 1]
        return cur.keys[len(cur.keys) - 1]

    def get_successor(self, x, i):
        cur = x.child[i + 1]
        while not cur.leaf:
            cur = cur.child[0]
        return cur.keys[0]

    def merge(self, x, i):
        t = self.t
        child = x.child[i]
        sibling = x.child[i + 1]
        child.keys.append(x.keys[i])
        child.keys.extend(sibling.keys)
        if not child.leaf:
            child.child.extend(sibling.child)
        x.keys.pop(i)
        x.child.pop(i + 1)
        if len(x.keys) == 0:
            self.root = child

    def fill(self, x, i):
        t = self.t
        if i != 0 and len(x.child[i - 1].keys) >= t:
            self.borrow_from_prev(x, i)
        elif i != len(x.child) - 1 and len(x.child[i + 1].keys) >= t:
            self.borrow_from_next(x, i)
        else:
            if i != len(x.child) - 1:
                self.merge(x, i)
            else:
                self.merge(x, i - 1)

    def borrow_from_prev(self, x, i):
        child = x.child[i]
        sibling = x.child[i - 1]

        child.keys.insert(0, x.keys[i - 1])
        x.keys[i - 1] = sibling.keys.pop()
        if not child.leaf:
            child.child.insert(0, sibling.child.pop())

    def borrow_from_next(self, x, i):
        child = x.child[i]
        sibling = x.child[i + 1]

        child.keys.append(x.keys[i])
        x.keys[i] = sibling.keys.pop(0)
        if not child.leaf:
            child.child.append(sibling.child.pop(0))

# File System Node (representing a file or folder)
class FileSystemNode:
    def __init__(self, name, node_type, t):
        self.name = name
        self.type = node_type

        if node_type == "folder":
            self.children = FileExplorer(t)
        else:
            self.children = None

# Main File System Class
class FileSystem:
    def __init__(self, t):
        self.t = t
        self.tree = FileExplorer(t)
        self.tree.root = BTreeNode(True)
        root_folder = FileSystemNode("root", "folder", self.t)
        self.tree.insert(("root", root_folder))

    def _path_str(self, path):
        if path:
           return '/'.join(path)
        return 'root'
    
    def _split_path(self, path =[]):
        if path:
            return path.split("/")
        else:
            return []
        
    def _find_node(self, path):
        current_node = self.tree.root.keys[0][1]
        if not path:
            return current_node

        current_btree_node = current_node.children.root
        node = None
        for segment in path:
            found = False
            next_btree_node = None
            for key_tuple in current_btree_node.keys:
                if key_tuple[0] == segment and key_tuple[1].type == "folder":
                    node = key_tuple[1]
                    next_btree_node = node.children.root
                    found = True
                    break
            if not found:
                return None
            current_btree_node = next_btree_node

        return node

    def _getParentNode(self, path):
        if path:
            parent_node = self._find_node(path)
        else:
            parent_node = self.tree.root.keys[0][1]

        if not parent_node or parent_node.type != "folder":
            print(f"\033[91m[Error] Path '{self._path_str(path)}' does not exist or is not a folder\033[0m")
            return None
        return parent_node

    def create_folder(self, folder_name, path=[], load=None):
        parent_node = self._getParentNode(path)
        if not parent_node:
            return

        for key, node in parent_node.children.root.keys:
            if key == folder_name:
                print(f"\033[91m[ERROR] A folder or file named '{folder_name}' already exists in '{self._path_str(path)}'\n\033[0m")
                return
        parent_node.children.insert((folder_name, FileSystemNode(folder_name, "folder", self.t)))

        if load is None:
            print(f"\033[34m[INFO] Folder '{folder_name}' created in {self._path_str(path)}\n\033[0m")

    def create_file(self, file_name, path=[], load=None):

        parent_node = self._getParentNode(path)
        if not parent_node:
            return

        for key, node in parent_node.children.root.keys:
            if key == file_name:
                print(f"\033[91m [ERROR] A file named '{file_name}' already exists in '{self._path_str(path)}'\n\033[0m")
                return

        parent_node.children.insert((file_name, FileSystemNode(file_name, "file", self.t)))

        if load is None: # Only print INFO if it's a new creation, not loading
            print(f"\033[34m[INFO] File '{file_name}' created in {self._path_str(path)}\n\033[0m")

    def _recursive_delete(self, node):
        if node.type != "folder" or not node.children:
            return

        keys_to_delete = [key_tuple[0] for key_tuple in node.children.root.keys]

        for key_name in keys_to_delete:
            found_child_node = None
            for key_tuple in node.children.root.keys:
                if key_tuple[0] == key_name:
                    found_child_node = key_tuple[1]
                    break

            if found_child_node:
                if found_child_node.type == "folder":
                    self._recursive_delete(found_child_node)
                    node.children.delete(node.children.root, key_name)
                elif found_child_node.type == "file":
                    node.children.delete(node.children.root, key_name)

    def delete_file(self, name, path=[]):
        parent_node = self._getParentNode(path)
        if not parent_node:
            return

        current_btree = parent_node.children.root

        found = False
        for i in range(len(current_btree.keys)):
            key, node = current_btree.keys[i]
            if key == name and node.type == "file":
                parent_node.children.delete(parent_node.children.root, name)
                print(f" \033[34m[INFO] Delete file '{name}' from {self._path_str(path)}\n\033[0m")
                found = True
                break

        if not found:
            print(f"\033[91m[Error]: File '{name}' not found in {self._path_str(path)}\033[0m")

    def delete_folder(self, name, path=[]):
        parent_node = self._getParentNode(path)
        if not parent_node:
            return

        current_btree = parent_node.children.root
        target_folder_node = None

        for i in range(len(current_btree.keys)):
            key, node = current_btree.keys[i]
            if key == name and node.type == "folder":
                target_folder_node = node
                break

        if not target_folder_node:
            print(f"\033[91m[Error]: Folder '{name}' not found in {self._path_str(path)}\033[0m")
            return

        self._recursive_delete(target_folder_node)

        parent_node.children.delete(parent_node.children.root, name)
        print(f"\033[34m[INFO] Delete folder '{name}' from {self._path_str(path)}\n\033[0m")

    def rename_node(self, old_name, new_name, path=[]):
        parent_node = self._getParentNode(path)
        if not parent_node:
            return

        current_btree = parent_node.children.root

        for existing_key, _ in current_btree.keys:
            if existing_key == new_name:
                print(f"\033[91m[Error]: '{new_name}' already exists in {self._path_str(path)}\033[0m")
                return

        found = False
        for i in range(len(current_btree.keys)):
            key, node = current_btree.keys[i]
            if key == old_name:
                parent_node.children.delete(parent_node.children.root, old_name)
                node.name = new_name
                parent_node.children.insert((new_name, node))
                print(f"\033[34m[INFO] Renamed '{old_name}' to '{new_name}' in {self._path_str(path)}\033[0m")
                found = True
                break

        if not found:
            print(f"\033[91m[Error]: '{old_name}' not found in {self._path_str(path)}\033[0m")

    def move_file(self, file_name, source_path=[], dest_path=[]):
        source_parent = self._getParentNode(source_path)
        if not source_parent: return

        dest_parent = self._getParentNode(dest_path)
        if not dest_parent: return

        file_node = None
        for i, (key, node) in enumerate(source_parent.children.root.keys):
            if key == file_name and node.type == "file":
                file_node = node
                break
        if not file_node:
            print(f"\033[91m[Error]: File '{file_name}' not found in {self._path_str(source_path)}\033[0m")
            return

        for key, node in dest_parent.children.root.keys:
            if key == file_name:
                print(f"\033[91m[Error]: '{file_name}' already exists in {self._path_str(dest_path)}\033[0m")
                return

        source_parent.children.delete(source_parent.children.root, file_name)

        dest_parent.children.insert((file_name, file_node))
        print(f"\033[34m[INFO] Moved file '{file_name}' from {self._path_str(source_path)} to {self._path_str(dest_path)}\033[0m")

    def move_folder(self, folder_name, source_path=[], dest_path=[]):
        source_parent = self._getParentNode(source_path)
        if not source_parent: return

        dest_parent = self._getParentNode(dest_path)
        if not dest_parent: return

        folder_node = None
        for i, (key, node) in enumerate(source_parent.children.root.keys):
            if key == folder_name and node.type == "folder":
                folder_node = node
                break
        if not folder_node:
            print(f"\033[91m[Error]: Folder '{folder_name}' not found in {self._path_str(source_path)}\033[0m")
            return

        for key, node in dest_parent.children.root.keys:
            if key == folder_name:
                print(f"\033[91m[Error]: Folder '{folder_name}' already exists in {self._path_str(dest_path)}\033[0m")
                return

        source_parent.children.delete(source_parent.children.root, folder_name)

        dest_parent.children.insert((folder_name, folder_node))
        print(f"\033[34m[INFO] Moved folder '{folder_name}' from {self._path_str(source_path)} to {self._path_str(dest_path)}\033[0m")

    def _display(self, node, prefix=""):
        total = len(node.keys)
        for i, (name, node) in enumerate(node.keys):
            connector = "    " if i == total - 1 else "    "
            node_type = node.type
            print(f"{prefix}{connector}{name} ({node_type})")

            if node_type == "folder" and node.children:
                extension = "    " if i == total - 1 else "    "
                self._display(node.children.root, prefix + extension)

    def display_tree(self):
        print("\n\033[34m==== [File System Structure]====\n")
        root_node = self.tree.root.keys[0][1]
        print("root/")
        if root_node.children and root_node.children.root.keys:
            self._display(root_node.children.root, prefix="")
        else:
            print("  (Root folder is empty)")
        print("\033[0m\n")

    def _search_recursive(self, node, target_name, current_path, results, target_type):
        for key, fsnode in node.keys:
            path_now = current_path + [key]
            if key == target_name and fsnode.type == target_type:
                results.append((fsnode, path_now))

            if fsnode.type == "folder":
                self._search_recursive(fsnode.children.root, target_name, path_now, results, target_type)

    def search_file(self, file_name):
        results = []
        root_node = self.tree.root.keys[0][1]
        self._search_recursive(root_node.children.root, file_name, ["root"], results, "file")

        if not results:
            print(f" [INFO] No file named '{file_name}' found.")
        else:
            print(f" [INFO] Search results for file '{file_name}':")

            for fsnode, path in results:
                print(f"Path: {'/'.join(path)}")
                

    def search_folder(self, folder_name):
        results = []
        root_node = self.tree.root.keys[0][1]
        self._search_recursive(root_node.children.root, folder_name, ["root"], results, "folder")

        if not results:
            print(f" [INFO] No folder named '{folder_name}' found.")
        else:
            print(f" [INFO] Search results for folder '{folder_name}':")

            for fsnode, path in results:
                print(f"Path: {'/'.join(path)}")

    def _get_flat_representation(self, node, current_path, flat_list):

        for key, fs_node in node.keys:
            full_path = current_path + [key]
            parent_path_str = '/'.join(current_path[1:]) if len(current_path) > 1 else "" # Exclude "root" from parent path

            flat_list.append({

                "type": fs_node.type,
                "name": fs_node.name,
                "parent_path": parent_path_str, 

            })
            if fs_node.type == "folder" and fs_node.children:
                self._get_flat_representation(fs_node.children.root, full_path, flat_list)


    def save_state(self, filename='Data_set.txt'):

        flat_list = []
        root_fs_node = self.tree.root.keys[0][1]

        if root_fs_node.children and root_fs_node.children.root.keys:
            self._get_flat_representation(root_fs_node.children.root, ["root"], flat_list)

        with open(filename, 'w') as f:
            for entry in flat_list:
                line = f"{entry['type']},{entry['name']},{entry['parent_path']}\n"
                f.write(line)

        print(f" File system state saved to '{filename}'")

    @staticmethod
    def load_state(filename='Data_set.txt', t_value=6):

        if os.path.exists(filename):
            fs = FileSystem(t_value) 
            entries_to_process = []
            with open(filename, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 3:
                        entry_type, name, parent_path_str = parts
                        entries_to_process.append({
                            "type": entry_type,
                            "name": name,
                            "parent_path": parent_path_str,
                        })

            for entry in entries_to_process:
                parent_path_list = entry['parent_path'].split('/') if entry['parent_path'] else []
                if entry['type'] == 'folder':
                    fs.create_folder(entry['name'], parent_path_list, load = True )
                elif entry['type'] == 'file':
                    fs.create_file(entry['name'], parent_path_list, load = True )

            print(f" File system state loaded from '{filename}'")
            return fs
        else:
            print(f" No saved file system state found at '{filename}'. Creating a new one.")
            return None
        

        

    def menu(self):
        print("="*45)
        print("** FILE SYSTEM MENU **".center(42))
        print("="*45)

        box_width = 43
        top_bottom = "+" + "-" * box_width + "+"
        menu_text = (
            top_bottom + "\n" +
            "| {:<20} {:<20} |\n".format("A. Create folder", "B. Create file") +
            "| {:<20} {:<20} |\n".format("C. Delete folder", "D. Delete file") +
            "| {:<20} {:<20} |\n".format("E. Rename folder", "F. Rename file") +
            "| {:<20} {:<20} |\n".format("G. Move folder", "H. Move file") +
            "| {:<20} {:<20} |\n".format("I. Search folder", "J. Search file") +
            "| {:<20} {:<20} |\n".format("K. Display File Explorer", "") +
            "| {:<20} {:<20} |\n".format("M. Menu","L. Exit") +
            top_bottom
        )
        print(menu_text)

        while True:
            choice = input("\n-> Enter your choice: ").strip().upper()

            if choice == "A":
                folder_name = input("[INPUT] Folder name: ").strip()
                path = input("[INPUT] Path (e.g., projects/python) [leave empty for root]: ").strip()
                path_list = self._split_path(path)
                self.create_folder(folder_name, path_list)
                print("\n")

            elif choice == "B":
                file_name = input("[INPUT] File name: ").strip()
                path = input("[INPUT] Path: ").strip()
                path_list = self._split_path(path)
                self.create_file(file_name, path_list)
                print("\n")

            elif choice == "C":
                folder_name = input("[INPUT] Folder name to delete: ").strip()
                path = input("[INPUT] Parent path: ").strip()
                path_list = self._split_path(path)
                self.delete_folder(folder_name, path_list)
                print("\n")

            elif choice == "D":
                file_name = input("[INPUT] File name to delete: ").strip()
                path = input("[INPUT] Parent path: ").strip()
                path_list = self._split_path(path)
                self.delete_file(file_name, path_list)
                print("\n")

            elif choice == "E":
                old_name = input("[INPUT] Old folder name: ").strip()
                new_name = input("[INPUT] New folder name: ").strip()
                path = input("[INPUT] Parent path: ").strip()
                path_list = self._split_path(path)
                self.rename_node(old_name, new_name, path_list)
                print("\n")

            elif choice == "F":
                old_name = input("[INPUT] Old file name: ").strip()
                new_name = input("[INPUT] New file name: ").strip()
                path = input("[INPUT] Parent path: ").strip()
                path_list = self._split_path(path)
                self.rename_node(old_name, new_name, path_list)
                print("\n")

            elif choice == "G":
                folder_name = input("[INPUT] Folder name to move: ").strip()
                source_path = input("[INPUT] Source path (ex: projects/python) [leave empty for root]: ").strip()
                dest_path = input("[INPUT] Destination path (ex: documents) [leave empty for root]: ").strip()
                source_path_list = self._split_path(source_path)
                dest_path_list = self._split_path(dest_path)
                self.move_folder(folder_name, source_path_list, dest_path_list)
                print("\n")

            elif choice == "H":
                file_name = input("[INPUT] Enter file name to move: ").strip()
                source_path = input("[INPUT]  Enter source path (ex: projects/python) [leave empty for root]: ").strip()
                dest_path = input("[INPUT] Enter destination path (ex: documents) [leave empty for root]: ").strip()
                source_path_list = self._split_path(source_path)
                dest_path_list = self._split_path(dest_path)
                self.move_file(file_name, source_path_list, dest_path_list)
                print("\n")

            elif choice == "I":
                folder_name = input("[INPUT] Enter folder name to search: ").strip()
                self.search_folder(folder_name)
                print("\n")

            elif choice == "J":
                file_name = input("[INPUT] Enter file name to search: ").strip()
                self.search_file(file_name)
                print("\n")

            elif choice == "K":
                print("\n")
                self.display_tree()

            elif choice == "L":
                Save_state = input("Do you want to save the File System state [Y/N]: ")
                if Save_state[:1] == "y" or Save_state[:1] == "Y":
                    self.save_state(FILE) # Save state on exit
                print("\n ...Exiting the file system")

                break

            elif choice == "M":
                print(menu_text)

            else:
                print("\033[91m[Error] Invalid choice. Please try again.\033[0m")

            print(end="")


FILE = 'Data_set.txt'
DEFAULT_B_TREE_DEGREE = 6
fs = None

A = input("Do you want to load save [Y/N]:")
if A[:1] == "Y" or A[:1] == "y":
    fs = FileSystem.load_state(FILE)

if fs is None:
    fs = FileSystem(t=DEFAULT_B_TREE_DEGREE)
    print("Initializing a new file system with default structure.")
    print("\n--- Initial File System State ---")
    fs.display_tree()
else:
    print("\n--- Loaded File System State ---")
    fs.display_tree()


# Start the interactive menu
fs.menu()
