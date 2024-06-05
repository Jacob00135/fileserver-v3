(() => {
    'use strict';

    const uploadInfo = document.querySelector('main .upload-info');
    const fileInput = document.getElementById('files');
    const uploadForm = document.querySelector('form[name="upload"]');

    fileInput.addEventListener('input', selectFile);
    uploadForm.addEventListener('submit', uploadFile);

    function checkFileSize(files) {
        const maxSize = 4 * 1024 * 1024 * 1024;
        for (let i = 0; i < files.length; i++) {
            if (files[i].size > maxSize) {
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
            alert("上传的单个文件大小不允许超过4G！");
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

    function postFile(files, result, callback) {
        const i = result.length;

        // 使用AJAX发送请求
        const url = uploadForm.getAttribute('action');
        const form = new FormData();
        const xhr = new XMLHttpRequest();
        form.append('file', files[i]);

        // 设置上传文件的进度
        const progressText = uploadInfo.querySelectorAll('li > .progress')[i];
        const progressBar = progressText.parentNode;
        xhr.upload.addEventListener('progress', (e) => {
            if (!e.lengthComputable) {
                return undefined;
            }

            const rate = Math.floor((e.loaded / e.total) * 100);
            progressText.innerHTML = rate + '%';
            progressBar.style.backgroundSize = rate + '%';
        });

        // 发送请求并处理响应
        xhr.addEventListener('readystatechange', (e) => {
            if (xhr.readyState !== 4 || xhr.status !== 200) {
                return undefined;
            }

            const response = JSON.parse(xhr.responseText);

            if (response.status === 1) {
                progressText.innerHTML = '成功';
                result.push({'status': 1, 'message': '上传成功'});
            } else {
                progressText.innerHTML = '失败';
                result.push({'status': 0, 'message': response.message});

                const messageLi = document.createElement('li');
                messageLi.innerHTML = response.message;
                uploadInfo.insertBefore(messageLi, progressBar.nextElementSibling);
            }

            if (i + 1 < files.length) {
                postFile(files, result, callback);
            } else {
                callback && callback(result);
            }
        })
        xhr.open('post', url, true);
        xhr.send(form);
    }

    function uploadFile(e) {
        e.preventDefault();

        const files = fileInput.files;

        if (!checkFileSize(files)) {
            alert("上传的单个文件大小不允许超过4G！");
            return undefined;
        }

        postFile(files, []);
    }
})();