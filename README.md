# B-Tree-File-System-Simulation
### Members:
- Le Dang Thanh Binh - 20233892
- Nguyen Huy Dat - 20233894
- Nguyen Viet Dung - 20224360

## Introduction
The following project is about building a simple File Explorer Simulation using B-Tree. 
The programm will allow the user to create, delete, move, display and browse through file / folder in a simulated File Explorer.
When the program is terminated, the user can choose to save the simulated file and folder. 

## Design of the file System
Program used - Python\
Used data structures, algorithm - B-Tree, Depth-first search\

## Implementation - Algorithms of the System
Mainly there are 6 functions:
1. Create file/folders
2. Delete file/folders
3. Search file/folders
4. Move file/folders
5. Rename file/folders
6. Display File Explorer

**1.Create file/folders**

      Step 1: Get parent folder from the path directory
      Step 2: Insert the file/folder to the subtree of the parent node
      
**2.Delete file/folders**

      Step 1: Get the parent folder from the path directory
      Step 2: Find the file/folder to delete from the B-Tree
      Step 3(*): If it is folder, recursively delete its sub file/folder
      Step 4: Delete File/Folder
      
**3.Search file/folders**

      Step 1: Start at root folder
      Step 2: Recursively search the File System using depth-first-search algorithm
      Step 3: Print out Result
      
**4.Move file/folders**

      Step 1: Find the source parent folder and destination parent folder from the path directory
      Step 2(*): If it is move folders, Find the sub files/folders to move along with the source folder
      Step 3: Check for name conflict in the destination folder
      Step 4: Delete the folder from the source folder
      Step 5: Insert the folder into the destination folder

**5.Rename file/folders**

      Step 1: Get the parent folder from the path directory
      Step 2: Check if the new name already existed in the current folder
      Step 3: Delete the file/folder with the old name
      Step 4: Insert the file/folder with the new name
      
**6.Display the File Explorer**

      Display the enter File System using list directory

## Instructions to run program

1. **Install Compiler**
Make sure you have Python or the neccessary IDE install

2. **Compile the program
Run the following command to compile the program

      Python persistent_BTFS.py

## Video demo


 
