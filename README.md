# Super Simple Cloud
### The simplest way to turn an idle computer + some form of storage into a personal cloud
Got some flash drives sitting around doing nothing? Use them as a way to get free personal cloud storage! Super Simple Cloud will provide you with a simple to use interface from where you can manage your files, folders, make backups and set up file recovery using the Reed Solomon algorithm!

**⚠️Please also keep in mind that this not very secure and should not be used for storing sensitive information.⚠️**

## How to set up Super Simple Cloud
If you are on a Debian based linux distro:
1. Download the install.sh script with `wget https://raw.githubusercontent.com/DevMa7e1/SuperSimpleCloud/refs/heads/main/install.sh`
2. Run the command `chmod +x install.sh` to make the file executable
3. Run the file `./install.sh` **and you're done!** <sup>very simple indeed</sup>

#### To run Super Simple Cloud after closing it, you can just type the command `./start.sh` from inside the SuperSimpleCloud-main folder.

If you are using a non Debian based distro or Windows, [**check out the how2install guide**](https://github.com/DevMa7e1/SuperSimpleCloud/blob/main/how2install.md).

## Things you might want to know about Super Simple Cloud

1. **Different colored items are different things**<br>

(white) **text.txt** -> Normal file<br>
(gray) <span style="color: gray;">**text.txt**</span> -> Backup file<br>
(green) <span style="color: lime;">**text.txt**</span> -> Encrypted file<br>
(blue) <span style="color: lightblue;">**text.txt**</span> -> Recovery file<br>
(orange) <span style="color: orange;">**folder**</span> -> folder<br>

2. **Clicking on colored files does something different**

(white) **text.txt** -> Download file<br>
(gray) <span style="color: gray;">**text.txt**</span> -> Download from backup<br>
(green) <span style="color: lime;">**text.txt**</span> -> Decrypt file<br>
(blue) <span style="color: lightblue;">**text.txt**</span> -> Recover file<br>
(orange) <span style="color: orange;">**folder**</span> -> Navigate to folder<br>

3. **You can change different settings by editing the setup.txt file**

**reedsolo** -> Reed Solomon nysm (default 32)(use 8 or 4 for large files)<br>
**autorecover** -> (1 or 0) If the cloud should automatically set up a recovery file when uploading a file (very slow for files > 50 MB)<br>
**autobackup** -> (1 or 0) If the cloud should automatically make a backup when uploading a file

4. **Reed Solomon based actions are slow**

If you are using Reed Solomon based backups, please keep in mind that they are very slow when file size is bigger than 50MB and quite slow at 10MB-50MB. To speed up big files quite a bit, edit the reedsolo line in the setup.txt file to a smaller power of 2 (like 16, 8, 4 or 2). **Please keep in mind that reducing the reedsolo value decreases the ability to correct errors.** Also, for the impatient ones, you can check the live python server output for progress made on setting up and recovery. <sup>Thankfully this runs in the background so you can still interact with the cloud in the mean time.</sup>

5. **Don't store sensitive information without encrypting it**

Don't store any sensitive information on a cloud running Super Simple Cloud! But, if you insist, make sure to encrypt the file containing the sensitive information then <span style="color: red;">
**delete the original**</span> (white colored one). <sup>Actually the AES encryption is pretty strong, if you use a good password!</sup>

