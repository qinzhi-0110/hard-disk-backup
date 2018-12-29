# hard-disk-backup
hard-disk-backup, check new file and update to mobile hard disk

只需要分别指定源路径和目标路径即可实现目录下所有文件的增量复制

如果一个文件在源路径下存在而目标路径下不存在，则直接复制

如果一个文件在源路径和目标路径都存在，则对比是否相同，如果相同不复制，不同则更新目标路径下的文件。

