var photosp = 0;
var photolisting_num = 5;
var photoep = photolisting_num;
var photodatas;
var isfirst = true;
var isimageEnd = false;

$(document).ready(function () {
    var tagParam = GetURLParameter('tag');
    $("#Photos a").click(function () {
        getPhotoDatas($('#Photo'), tagParam);
        return false;
    });
    getPhotoDatas($('#Photo'), tagParam);
    
    $(window).scroll(function(){
        if($(window).scrollTop() == $(document).height()-$(window).height()){
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
        });
        window.isfirst = false;
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
        if(tag == null){
            addimgdivs = "<div class='photogrid captionfull'>";
            addimgdive = "<a href='/?tag="+ps[i].tag+"'><div class='cover boxcaption'>"+
                    "<p>"+ps[i].tagname+ "</p>"+
                    updateTagComment(ps[i])+
//                    "<p>"+ps[i].tagcomment+ "</p>"+
//                    updateTagComment()+
                    "</div></a>"+
                         "</div>";
        }else{
            addimgdivs = "<div class='photogrid captionfull'>";
            addimgdive = "<div class='cover boxcaption'>"+
                    "<p>"+ps[i].imagecomment+ "</p>"+
                    "</div>"+
                         "</div>";
        }
        var addimg = addimgdivs+
                "<img src='/imageview/" + ps[i].imagekey + "' width='980px' id='" + imgid + "' alt='"+ps[i].tagname+"'/>"+
                addimgdive;
        nobj.append(addimg);
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
    editmode();
}
function updateTagComment(ps){
    if(ps.isadmin == 1){
        str = "<div class='tagcomment'>";
        str += ps.tagcomment;
        str += "<a href='#none'>admin</a>";
        str += "</div>";
        
        $(".tagcomment a",this).click(function(){
                $(this).append("clicked");
        });
        return str;
    }
    else
        return "<div class='tagcomment'>"+ps.tagcomment+ "</div>";
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