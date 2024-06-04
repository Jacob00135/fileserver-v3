(() => {
    'use strict';

    const uploadInfo = document.querySelector('main .upload-info');
    const fileInput = document.getElementById('files');
    fileInput.addEventListener('input', selectFile);

    function checkFileSize(files) {
        for (let i = 0; i < files.length; i++) {
            const sizeG = files[i].size / 1024 / 1024 / 1024;
            if (sizeG > 4) {
                return false;
            }
        }

        return true;
    }

    function fileSizeTransform(size) {
        const unitArr = ['B', 'KB', 'MB', 'GB'];
        for (let i = 0; i < unitArr.length; i++) {
            if (size >= 1024) {
                size = size / 1024;
            } else {
                return size.toFixed(2) + ' ' + unitArr[i];
            }
        }
    }

    function selectFile(e) {
        uploadInfo.innerHTML = '';
        const files = fileInput.files;

        if (!checkFileSize(files)) {
            alert("上传的单个文件不允许超过4G！");
            return undefined;
        }

        // 添加文件信息
        for (let i = 0; i < files.length; i++) {
            let name = files[i].name;
            let size = fileSizeTransform(files[i].size);
            let li = document.createElement('li');
            li.innerHTML = `
                <div class="filename">${name}</div>
                <div class="size">${size}</div>
                <div class="progress">0%</div>
            `;
            uploadInfo.appendChild(li);
        }
    }
})();