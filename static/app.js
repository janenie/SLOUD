(function(){

    var cls = {};

    function new_process_xhr(handler){
        return function(){
            var xhr = new XMLHttpRequest();
            xhr.upload.addEventListener(
                "progress",
                function(evt){
                if (evt.lengthComputable) {  
                    handler(evt.loaded / evt.total);
                }
                }, false);
            return xhr;
        }
    }

    cls.IndexFileUploader = function(self, data){
        var short_d = $('[name=short]', self);
        var desc_d = $('textarea', self);
        var url = self.attr('action');
        var submit_d = $('[type=submit]', self);
        var fc_d = $('[type=file]', self);
        $('.filechooser', self).on('filechoose', function(e, d){
            short_d.val(d.name);
            $('textarea', self).focus();
            desc_d.text('文件： '+d.name+' ');
        });
        self.submit(function(e){
            e.preventDefault();
            if(!fc_d[0].files[0]){
                alert('请选择一个文件！')
                return false;
            }
            if(!short_d.val()){
                alert('请输入一个地址！');
                return false;
            }
            submit_d.addClass('disabled');
            $.ajax({
                url: url,
                type: 'POST',
                data: new FormData(self[0]),
                processData: false,
                contentType: false,
                xhr: new_process_xhr(function(p){
                    submit_d.val((p*100).toFixed(2)  + '%');
                    if(p==1){
                        submit_d.val('等待服务器处理中...');
                    }
                }),
                success: function(data){
                    if(data.ok){
                        alert('上传成功！');
                        location = data.location;
                    }else{
                        if(data.code==1) {
                            submit_d.removeClass('disabled').val('开始上传！');
                            alert('不能使用相同的网址名');
                            short_d.focus();
                        }
                        else alert('上传失败');
                    }
                }
            });
            return false;
        });                
    }

    cls.UpdateFileUploader = function(self){
        var url = self.attr('action');
        var submit_d = $('[type=submit]', self);
        var fc_d = $('[type=file]', self);
        self.submit(function(e){
            e.preventDefault();
            if(!fc_d[0].files[0]){
                alert('你还没选择一个文件！');
                return false;
            };
            submit_d.addClass('disabled');
            $.ajax({
                url: url,
                type: 'POST',
                data: new FormData(self[0]),
                processData: false,
                contentType: false,
                xhr: new_process_xhr(function(p){
                    submit_d.val((p*100).toFixed(2)  + '%');
                    console.log(p);                    
                    if(p==1){
                        submit_d.val('等待服务器处理中...');
                    }
                }),
                success: function(data){
                    if(data.ok){
                        alert('上传成功！');
                        location.hash = "";
                        location.hash = "#main";
                        location.reload(true);
                    }else{
                        alert('上传失败');
                    }
                }
            });
            return false;
        });
    }

    cls.ResDeleter = function(self){
        var short = self.data('short');
        var url = self.data('action');
        var deleted = false;
        self.click(function(){
            if(deleted) return;
            deleted = true;
            $.post(url, { short: short },
                   function(data){
                       if(data.ok){
                           alert('删除成功！');
                           location = data.location;
                       }else{
                           alert('删除失败！');
                       }
                   });
        });
    }

    $(function(){
        $('.prefixinputer').each(function(){
            var self=$(this);
            var prefix = self.data('prefix');
            var prefix_d = $('<span class="prefix">'+prefix+'</span>');         
            self.append(prefix_d);
            $('input', self).css({
                'paddingLeft' : ''+(15 + prefix_d.width()) + 'px'
            });                
        });
        $('.filechooser').each(function(){
            var self = $(this);
            var input_d = $('input', self);
            var filename_d = $('.filename', self);
            input_d.change(function(){
                filename_d.text(this.files[0].name);
                self.trigger('filechoose', this.files[0]);
            });
        });
        $('.controller').each(function(){
            var self = $(this);
            var clsname = self.data('cls');
            cls[clsname](self, self.data());
        });
    });

})();
