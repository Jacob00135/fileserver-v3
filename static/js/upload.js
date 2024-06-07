(() => {
    'use strict';

    const uploadInfo = document.querySelector('main .upload-info');
    const fileInput = document.getElementById('files');
    const uploadForm = document.querySelector('form[name="upload"]');

    fileInput.addEventListener('input', selectFile);
    uploadForm.addEventListener('submit', submitUploadFormEvent);

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

    function submitUploadFormEvent(e) {
        e.preventDefault();

        // 用到的变量
        const files = fileInput.files;

        // 检查文件的大小是否符合要求
        if (!checkFileSize(files)) {
            alert('上传的单个文件大小不允许超过4G！');
            return undefined;
        }

        // 上传所有文件
        uploadAllFile(files, [], (result) => {
            console.log(result);
        });
    }

    function uploadAllFile(files, result, callback) {
        // 设置默认参数
        if (result === undefined) {
            result = [];
        }

        /**
         * 1. 发送请求，检查文件是否已存在
         * 2. 若1的请求失败，显示错误级别信息，然后进行下一个文件的上传
         * 3. 若1的请求成功，且文件存在，显示警告“已有同名文件”，然后进行下一个文件的上传
         * 4. 若1的请求成功，且文件不存在，发送上传文件的请求
         * 5. 若4的请求失败，显示错误级别信息，然后进行下一个文件的上传
         * 6. 若4的请求成功，则直接进行下一个文件的上传
         */

        // 检查是否已经满足退出条件
        if (result.length >= files.length) {
            callback && callback(result);
            return undefined;
        }

        // 获取本次用到的变量
        const i = result.length;
        const file = files[i];
        const progressBar = uploadInfo.querySelectorAll('li:not(.hint-message)')[i];
        const progressText = progressBar.querySelector('.progress');

        // 1. 发送请求，检查文件是否已存在
        ajaxFileExists(file.name, (fileExistsResponse) => {
            // 2. 第1步的请求失败，显示错误级别信息，然后进行下一个文件的上传
            if (fileExistsResponse.status === 0) {
                progressText.innerHTML = '失败';
                insertHintMessageBlock(i, fileExistsResponse.message, 'error');
                result.push({'status': 0, 'message': fileExistsResponse.message});
                uploadAllFile(files, result, callback);
                return undefined;
            }

            // 3. 第1步的请求成功，且文件存在，显示警告“已有同名文件”，然后进行下一个文件的上传
            if (fileExistsResponse.data === 1) {
                progressText.innerHTML = '失败';
                insertHintMessageBlock(i, '已有同名文件', 'warning');
                result.push({'status': 0, 'message': '已有同名文件'});
                uploadAllFile(files, result, callback);
                return undefined;
            }

            // 4. 第1步的请求成功，且文件不存在，则发送上传文件的请求
            ajaxUploadFile(file, (rate) => {
                // 上传文件时，实时显示文件的上传进度
                progressBar.style.backgroundSize = rate + '%';
                progressText.innerHTML = rate + '%';
            }, (uploadFileResponse) => {
                // 5. 若第4步的请求失败，显示错误级别信息，然后进行下一个文件的上传
                if (uploadFileResponse.status === 0) {
                    progressText.innerHTML = '失败';
                    insertHintMessageBlock(i, uploadFileResponse.message, 'error');
                    result.push({'status': 0, 'message': uploadFileResponse.message});
                    uploadAllFile(files, result, callback);
                    return undefined;
                }

                // 6.若第4步的请求成功，显示成功，然后进行下一个文件的上传
                progressText.innerHTML = '成功';
                result.push({'status': 1, 'message': '成功'});
                uploadAllFile(files, result, callback);
            });
        });
    }

    function insertHintMessageBlock(index, message, messageLevel) {
        // 设置默认参数
        if (messageLevel === undefined) {
            messageLevel = 'warning';
        }

        // 检查参数的合法性
        if (messageLevel !== 'warning' && messageLevel !== 'error') {
            throw `messageLevel参数不合法：${messageLevel}`;
            return undefined;
        }

        // 生成提示信息的块
        const hintMessageBlock = document.createElement('li');
        hintMessageBlock.innerHTML = message;
        hintMessageBlock.className = `hint-message ${messageLevel}`;

        // 在索引号为index的块之后插入提示信息（index从0开始编号）
        const child = uploadInfo.querySelectorAll('li:not(.hint-message)')[index + 1];
        uploadInfo.insertBefore(hintMessageBlock, child);
    }

    function ajaxFileExists(filename, callback) {
        // 获取发送请求的地址
        const srcFileExistsUrl = uploadForm.getAttribute('data-file-exists-url');
        let fileExistsUrl = decodeURIComponent(srcFileExistsUrl);
        if (fileExistsUrl.endsWith('/') || fileExistsUrl.endsWith('\\')) {
            fileExistsUrl = fileExistsUrl.slice(0, fileExistsUrl.length - 1);
        }
        fileExistsUrl = `${fileExistsUrl}\\${filename}`;

        // 注册处理响应的事件
        const xhr = new XMLHttpRequest();
        xhr.addEventListener('readystatechange', (e) => {
            if (xhr.readyState !== 4 || xhr.status !== 200) {
                return undefined;
            }

            const response = JSON.parse(xhr.responseText);
            callback && callback(response);
        });

        // 发送请求
        xhr.open('get', fileExistsUrl, true);
        xhr.send();
    }

    function ajaxUploadFile(file, progressCallback, responseCallback) {
        // 获取请求网址
        const url = uploadForm.getAttribute('action');

        // 将文件对象处理成可发送的数据对象
        const formData = new FormData();
        formData.append('file', file);

        // 注册处理文件上传进度的事件
        const xhr = new XMLHttpRequest();
        xhr.upload.addEventListener('progress', (e) => {
            if (!e.lengthComputable) {
                return undefined;
            }

            const rate = Math.floor((e.loaded / e.total) * 100);
            progressCallback && progressCallback(rate);
        });

        // 注册处理响应的事件
        xhr.addEventListener('readystatechange', (e) => {
            if (xhr.readyState !== 4 || xhr.status !== 200) {
                return undefined;
            }

            const response = JSON.parse(xhr.responseText);
            responseCallback && responseCallback(response);
        });

        // 发送请求
        xhr.open('post', url, true);
        xhr.send(formData);
    }

    /*
    function fileExists(filename, callback) {
        // 获取发送请求的地址
        let fileExistsUrl = decodeURIComponent(uploadForm.getAttribute('data-file-exists-url'));
        if (fileExistsUrl.endsWith('/') || fileExistsUrl.endsWith('\\')) {
            fileExistsUrl = fileExistsUrl.slice(0, fileExistsUrl.length - 1);
        }
        fileExistsUrl = `${fileExistsUrl}\\${filename}`;

        // 注册处理请求的事件
        const xhr = new XMLHttpRequest();
        xhr.addEventListener('readystatechange', (e) => {
            if (xhr.readyState !== 4 || xhr.status !== 200) {
                return undefined;
            }

            const response = JSON.parse(xhr.responseText);
            callback && callback(response);
        });
    }

    function postFile(files, result, callback) {
        const i = result.length;
        const file = files[i];
        const progressText = uploadInfo.querySelectorAll('li > .progress')[i];
        const progressBar = progressText.parentNode;

        // 检查文件是否存在
        fileExists(file.name, (response) => {
            if (response.status === 0) {
                const messageLi = document.createElement('li');
                messageLi.innerHTML = response.message;
                uploadInfo.insertBefore(messageLi, progressBar.nextElementSibling);
            } else {

            }
        });

        // 使用AJAX发送请求
        const url = uploadForm.getAttribute('action');
        const form = new FormData();
        const xhr = new XMLHttpRequest();
        form.append('file', file);

        // 设置上传文件的进度
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
        });
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
    */
})();