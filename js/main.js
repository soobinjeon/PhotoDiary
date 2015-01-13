var photosp = 0;
var photolisting_num = 5;
var photoep = photolisting_num;
var photodatas;
var isfirst = true;
var isimageEnd = false;
var iscommentupdating = false;
var isphotodeleting = false;

$(document).ready(function () {
    var tagParam = GetURLParameter('tag');
    $("#Photos a").click(function () {
        getPhotoDatas($('#Photo'), tagParam);
        return false;
    });
    getPhotoDatas($('#Photo'), tagParam);
    
    $(window).scroll(function(){
        if($(window).scrollTop() >= ($(document).height() * 0.9)-$(window).height()){
            getPhotoDatas($('#Photo'), tagParam);
            return false;
        }
    });
});

//Photo Image Control Function
function getPhotoDatas(obj,tag) {
    if(window.isfirst == true){
        var posting = $.post('/', {
            'request': 'photos',
            'photo_tag': tag
        });
        posting.done(function (data) {
            photodatas = $.parseJSON(data);
            //alert("te : "+photodatas.length);
            printPhotos(obj,tag);
            window.isfirst = false;
        });
    }else{
        printPhotos(obj,tag);
    }
}

//Print Photo Images
function printPhotos(obj,tag){
    var ps = window.photodatas;
    var looplength = photosp + photolisting_num;
    if(looplength > ps.length){
        looplength = ps.length;
        window.isimageEnd = true;
    }
    
    for (var i = window.photosp; i < looplength; i++){
        var nodeid = "imgnode" + (i);
        var imgid = "img" + (i);
        var nobj = $("<p></p>").attr('id', nodeid).appendTo(obj);
        $("<p><img src='css/upload/images/loading2.gif' width='100'/></p>").attr('class', 'loading').appendTo(nobj);
        var addimgdivs;
        var addimgdive;
        
        //write tag comment
        if(i == window.photosp && tag != null && ps != null && window.isfirst == true){
            var cmtwrap = $("#TagCommentWrap");
            var titlestr = "<h1>" + ps[0].tagname + "</h1>";
            if (ps[i].isadmin == 1) 
                titlestr += "<p id='admintag_"+ps[i].imagekey+"'><a class='admintag' href='#none'>-delete tag-</a></p>";
            titlestr += "<p class='PhotoTagComment'>"+ps[0].tagcomment+"</p>";
            cmtwrap.append(titlestr);
        }
        
        if(tag == null){
            addimgdivs = "<div class='photogrid captionfull'>";
            addimgdive = "<a href='/?tag="+ps[i].tag+"'><div class='cover boxcaption'>"+
                    "<p>"+ps[i].tagname+ "</p>"+
                    AdminTagComment(ps[i])+
//                    "<p>"+ps[i].tagcomment+ "</p>"+
//                    updateTagComment()+
                    "</div></a>"+
                         "</div>";
                 //javascript:alert(document.body.innerHTML);
        }else{
            addimgdivs = "<div id='"+ps[i].imagekey+"'>";
            addimgdive = "<div >"+
                    "<p>"+ps[i].imagecomment+ "</p>"+
                    "</div>"+
                         "</div>";

            //Admin mode, if you want delete the selected picture
            addimgdivs += AdminPhotoMode(ps[i]);
            
        }
        var addimg = addimgdivs+
                "<img src='/imageview/" + ps[i].imagekey + "' width='980px' id='" + imgid + "' alt='"+ps[i].tagname+"'/>"+
                addimgdive;
        nobj.append(addimg);
        //javascript:alert(document.body.innerHTML);
        //prompt("Copy to clipboard: Ctrl+C, Enter", oArg.Document);
        TagCommentEvent(ps);
        DeletePhoto(ps[i]);
        DeleteTag(ps[i]);

        $(".tagcomment").hide(); //Hide Comment!
        nobj.children("div").children('img').hide();
        $("#" + imgid).load(function () {
            var nid = $(this)[0].id.split('img');
            $(this).hide();
            $("#imgnode" + nid[1] + " > .loading").hide();
            //$("#imgnode" + nid[1]).fadeIn(500);
            $(this).fadeIn(500);

        });
    }
    updateMoreOption();
    //$(this).fadeIn();
    photogrid();
    addPhotolist();
    //editmode();
}

function DeleteTag(tcps) {
    $("#admintag_"+tcps.imagekey+" > a").click(function () {
        if (confirm("Do you wnat to delete this Tag?")) {
            var posting = $.post('/upload/uploadimage', {
                'request': 'deletetag',
                'tagname': tcps.tag
            });
            posting.done(function (data) {
                window.location.href = '/';
            });
        }
    });
}
//photo admin mode
function AdminPhotoMode(tcps) {
    if (tcps.isadmin == 1) {
        return "<div id='deletephoto_"+tcps.imagekey+"'><a id='"+tcps.imagekey+"' href='#none'>(Delete Below Photo)</a></div>";
    } else
        return "";
}

function DeletePhoto(selectedps) {
    //$(".deletephoto > a").click(function () {
    $("#deletephoto_"+selectedps.imagekey).click(function (){
        var tc = $(this).parent(this).parent(this);
        if (confirm("delete photo?")) {
            var posting = $.post('/upload/uploadimage', {
                '_method': 'DELETE',
                'key': selectedps.imagekey
            });
            posting.done(function (data) {
                tc.remove();
            });
        }
    });
}

function findPSbyImageKey(ps, tn) {
    for (var i = 0; i < ps.length; i++) {
        if (ps[i].imagekey == tn)
            return ps[i];
    }
    return null;
}
/**
Tag Comment Text Box for Updating comment
*/
function TagCommentEvent(ps){
    $(".tagcomment > a").click(function(){
                //alert("count");
                var tc = $(this).parent(this);
                var tid = $(this).attr('id');
                var selectedps = findTagbyTagname(ps, tid);
                if(selectedps != null){
                    var str = "";
                    str = "<textarea class='phototextbox' row='4' cols='100'>"+selectedps.tagcomment+"</textarea>";
                    str += "<br/><button class='submit' type='submit' value='submit'>Update</button>";
                    str += "<button class='cancel' type='cancel' value='cancel'>Cancel</button>";
                    tc.html(str);
                    UpdateTagComment(tc, tid, selectedps);
                }
        });
}
//Print "Update Tag"
function AdminTagComment(tcps, comment) {
    tn = tcps.tag;
    commentid = "tagcomment_" + tcps.tag;
    var tcomment = "";
    if (comment == null)
        tcomment = tcps.tagcomment;
    else
        tcomment = comment;
    if(tcps.isadmin == 1){
        str = "<div id='" + commentid + "' class='tagcomment'>";
        //"+tcps.tagcomment+"
        str += tcomment + "</br>";
        str += "<a id='"+tn+"' href='#none'>Update Text<br/></a>";
        str += "</div>";
        return str;
    }
    else
        return "<div class='tagcomment'>" + tcomment + "</div>";
}

//update Tag Comment
function UpdateTagComment(tc, tid, selectedps) {
    $("#tagcomment_"+selectedps.tag+" > .submit").click(function () {
        var updatedtx = $("#tagcomment_" + selectedps.tag + " > .phototextbox").val();
        var posting = $.post('/upload/uploadimage', {
            'request': 'updatetagcomment',
            'tagname': selectedps.tag,
            'updatedcomment': updatedtx
        });
        posting.done(function (data) {
            tc.html(AdminTagComment(selectedps, updatedtx));
            TagCommentEvent(window.photodatas);
        });
       
    });

    $("#tagcomment_" + selectedps.tag + " > .cancel").click(function () {
        tc.html(AdminTagComment(selectedps));
        TagCommentEvent(window.photodatas);
    });
}
function findTagbyTagname(ps, tn){
    for(var i=0;i<ps.length;i++){
        if(ps[i].tag == tn)
            return ps[i];
    }
    return null;
}

function editmode(){
    $(".tagcomment a", this).click(function(){
            $(this).append("clicked");
    });
}
//update More Image Button
function updateMoreOption(){
    if(!window.isimageEnd)
        $("#Photos #moreimage").text("More Images..").css("font-weight","Bold");
    else
        $("#Photos #moreimage").text("");
}
function addPhotolist() {
    window.photosp = photosp + photolisting_num;
    window.photoep = photoep + photolisting_num;
}
function getPhotoSP() {
    return window.photolisting_num;
}
function GetURLParameter(sParam) {
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++) {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam) {
            return sParameterName[1];
        }
    }
    return null;
}

function photogrid(){
    /*$('.photogrid.slidedown').hover(function(){
        $(".cover", this).stop().animate({top:'-260px'},{queue:false,duration:300});
    }, function() {
        $(".cover", this).stop().animate({top:'0px'},{queue:false,duration:300});
    });
    //Horizontal Sliding
    $('.photogrid.slideright').hover(function(){
        $(".cover", this).stop().animate({left:'325px'},{queue:false,duration:300});
    }, function() {
        $(".cover", this).stop().animate({left:'0px'},{queue:false,duration:300});
    });
    //Diagnal Sliding
    $('.photogrid.thecombo').hover(function(){
        $(".cover", this).stop().animate({top:'260px', left:'325px'},{queue:false,duration:300});
    }, function() {
        $(".cover", this).stop().animate({top:'0px', left:'0px'},{queue:false,duration:300});
    });
    //Partial Sliding (Only show some of background)
    $('.photogrid.peek').hover(function(){
        $(".cover", this).stop().animate({top:'90px'},{queue:false,duration:160});
    }, function() {
        $(".cover", this).stop().animate({top:'0px'},{queue:false,duration:160});
    });*/
    //Full Caption Sliding (Hidden to Visible)
    $('.photogrid.captionfull').hover(function(){
        $(".cover", this).stop().animate({
            height:'40%','font-size':'15pt'
        },{
            queue:false,duration:160
            ,complete: function(){
                $(this).children('.tagcomment').fadeIn(500);
            }
        });
    }, function() {
        $(".cover", this).stop().animate({
            height:'30%','font-size':'50pt'
        },{
            queue:false,duration:160
            ,start: function(){
                $(this).children('.tagcomment').hide();
            }
        });
    });
    /*//Caption Sliding (Partially Hidden to Visible)
    $('.photogrid.caption').hover(function(){
        $(".cover", this).stop().animate({top:'160px'},{queue:false,duration:160});
    }, function() {
        $(".cover", this).stop().animate({top:'220px'},{queue:false,duration:160});
    });*/
}