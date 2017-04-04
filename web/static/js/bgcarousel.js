/* Background Image Carousel
* Created: Jan 17th, 2012 by DynamicDrive.com. This notice must stay intact for usage 
* Author: Dynamic Drive at http://www.dynamicdrive.com/
* Visit http://www.dynamicdrive.com/ for full source code
*/

//** Modified Jan 23th, 12'- Fixed bug with auto rotate bug in "manual" mode
//** Modified Feb 21st, 12'- Fixed bug with carousel not always initializing in IE8 and less
//** Modified June 26th, 14 to v1.1': Flexible carousel dimensions now supported, swipe to navigate added, plus other minor enhancements.
//** Modified June 27th, 14: Fixed nav buttons fade in/out issue

jQuery.noConflict()

function bgCarousel(options){
	var $=jQuery
	this.setting={displaymode:{type:'auto', pause:2000, stoponclick:false, cycles:2, pauseonmouseover:true}, activeslideclass:'selectedslide', orientation:'h', persist:true, slideduration:500} //default settings
	jQuery.extend(this.setting, options) //merge default settings with options
	this.setting.displaymode.pause+=400+this.setting.slideduration // 400ms is default fade in time
	var curslide=(this.setting.persist)? bgCarousel.routines.getCookie("slider-"+this.setting.wrapperid) : 0
	this.curslide=(curslide==null || curslide>this.setting.imagearray.length-1)? 0 : parseInt(curslide) //make sure curslide index is within bounds
	this.curstep=0
	this.animation_isrunning=false //variable to indicate whether an image is currently being slided in
	this.posprop=(this.setting.orientation=="h")? "left" : "top"
	options=null
	var slideshow=this, setting=this.setting, preloadimages=[], imagesloaded=0, slidesHTML=''
	for (var i=0, max=setting.imagearray.length; i<max; i++){ //preload images
		preloadimages[i]=new Image()
		$(preloadimages[i]).bind('load error', function(){
			imagesloaded++
			if (imagesloaded==max){ //when all images have preloaded
		$(function(){ //on document.ready
			slideshow.init($, slidesHTML)
		})
			}
		})
		preloadimages[i].src=setting.imagearray[i][0]
		slidesHTML+=bgCarousel.routines.getSlideHTML(setting, setting.imagearray[i], '100%', '100%', this.posprop)+'\n'
	}

	function positioncontrols($controls){
		var winwidth = $(window).outerWidth(),
				winheight = $(window).outerHeight(),
				controlwidth = $controls.eq(0).width(),
				controlheight = $controls.eq(0).height(),
				controltop, controlleft
				
		if (setting.orientation == 'h'){
			controltop = (setting.dimensions[1] > winheight)? winheight/2 : '50%'
			$controls.css({top: controltop, marginTop: -controlheight/2})
		}
		else if (setting.orientation == 'v'){
			controlleft = (setting.dimensions[0] > winwidth)? winwidth/2 : '50%'
			$controls.css({left: controlleft, marginLeft: -controlwidth/2})
		}
	}
	this.positioncontrols = positioncontrols

	$(window).bind('unload', function(){ //on window onload
		if (slideshow.setting.persist) //remember last shown slide's index?
			bgCarousel.routines.setCookie("slider-"+setting.wrapperid, slideshow.curslide)
	})

	$(window).bind('resize', function(){
		if (setting.dimensions){
			setting.dimensions=[slideshow.$wrapperdiv.width(), slideshow.$wrapperdiv.height()]
			positioncontrols(slideshow.$controls)
		}
	})

}

bgCarousel.prototype={

	slide:function(nextslide, dir){ //possible values for dir: "left", "right", "top", or "down"
		if (this.curslide==nextslide)
			return
		var slider=this, setting=this.setting
		var createobj=bgCarousel.routines.createobj
		var nextslide_initialpos=setting.dimensions[(dir=="right"||dir=="left")? 0 : 1] * ((dir=="right"||dir=="down")? -1 : 1)
		var curslide_finalpos=-nextslide_initialpos
		var posprop=this.posprop
		if (this.animation_isrunning!=null)
			this.animation_isrunning=true //indicate animation is running
		this.$imageslides.eq(nextslide).show().css(createobj([posprop, nextslide_initialpos], ['opacity', 0.5])) //show upcoming slide
			.stop().velocity(createobj([posprop, 0]), setting.slideduration, function(){
				var $this=jQuery(this)
				$this.addClass(setting.activeslideclass).velocity({opacity:1})
				.find('div.desc').stop().velocity({top:slider.descoffsettop, opacity: 1})
				slider.animation_isrunning=false
			})
			.find('div.desc').css({top: '-=100%', opacity: 0})

		this.$imageslides.eq(this.curslide)
			.removeClass(setting.activeslideclass)
			.stop().velocity(createobj([posprop, curslide_finalpos]), setting.slideduration, function(){
					var $this=jQuery(this)
					$this.hide()
			}) //hide outgoing slide

		this.curslide=nextslide
	},

	navigate:function(keyword){ //keyword: "back" or "forth"
		var slideshow=this, setting=this.setting
		clearTimeout(this.rotatetimer)
		if (!setting.displaymode.stoponclick && setting.displaymode.type!="manual"){ //if slider should continue auto rotating after nav buttons are clicked on
			this.curstep=(keyword=="back")? this.curstep-1 : this.curstep+1 //move curstep counter explicitly back or forth depending on direction of slide
			this.rotatetimer=setTimeout(function(){slideshow.rotate()}, setting.displaymode.pause)
		}
		var dir=(keyword=="back")? (setting.orientation=="h"? "right" : "down") : (setting.orientation=="h"? "left" : "up")	
		var targetslide=(keyword=="back")? this.curslide-1 : this.curslide+1
		targetslide=(targetslide<0)? this.$imageslides.length-1 : (targetslide>this.$imageslides.length-1)? 0 : targetslide //wrap around
		if (this.animation_isrunning==false)
			this.slide(targetslide, dir)
	},

	rotate:function(){
		var slideshow=this, setting=this.setting
		if (this.ismouseover){ //pause slideshow onmouseover
			this.rotatetimer=setTimeout(function(){slideshow.rotate()}, setting.displaymode.pause)
			return
		}
		var nextslide=(this.curslide<this.$imageslides.length-1)? this.curslide+1 : 0
		this.slide(nextslide, this.posprop) //go to next slide, either to the left or upwards depending on setting.orientation setting
		if (setting.displaymode.cycles==0 || this.curstep<this.maxsteps-1){
			this.rotatetimer=setTimeout(function(){slideshow.rotate()}, setting.displaymode.pause)
			this.curstep++
		}
	},

	init:function($, slidesHTML){
		var slideshow=this, setting=this.setting
		this.$wrapperdiv=$('#'+setting.wrapperid)
		setting.dimensions=[this.$wrapperdiv.width(), this.$wrapperdiv.height()]
		this.$wrapperdiv.css({position:'relative', visibility:'visible', overflow:'hidden', backgroundImage:'none'})
		if (this.$wrapperdiv.length==0){ //if no wrapper DIV found
			alert("Error: DIV with ID \""+setting.wrapperid+"\" not found on page.")
			return
		}
		this.$wrapperdiv.html(slidesHTML)
		this.$imageslides=this.$wrapperdiv.find('div.slide').hide()
		this.descoffsettop = this.$imageslides.eq(0).find('div.desc').css('top')
		this.$imageslides.eq(this.curslide).show()
			.css(bgCarousel.routines.createobj(['opacity', 0.5], [this.posprop, 0])) //set current slide's CSS position (either "left" or "top") to 0
			.addClass(setting.activeslideclass)
			.stop().velocity({opacity:1})
			.find('div.desc').css({top: '-=100%', opacity: 0}).velocity({top:this.descoffsettop, opacity: 1})
		var orientation=setting.orientation
		var controlpaths=(orientation=="h")? setting.navbuttons.slice(0, 2) : setting.navbuttons.slice(2)
		var $controls =  $('<img class="navbutton" src="'+controlpaths[1]+'" data-dir="forth" style="position:absolute; z-index:5; cursor:pointer; ' + (orientation=='v'? 'bottom:8px; left:46%' : 'top:46%; right:8px;') + '" />'
			+ '<img class="navbutton" src="'+controlpaths[0]+'" data-dir="back" style="position:absolute;z-index:5; cursor:pointer; ' + (orientation=='v'? 'top:8px; left:45%' : 'top:45%; left:8px;') + '" />'
		)
		.css({opacity:0})
		.click(function(){
			var keyword = this.getAttribute('data-dir')
			setting.curslide = (keyword == "right")? (setting.curslide == setting.content.length-1? 0 : setting.curslide + 1)
				: (setting.curslide == 0? setting.content.length-1 : setting.curslide - 1)
			slideshow.navigate(keyword)
		})
		this.$controls = $controls.appendTo(this.$wrapperdiv)
		this.positioncontrols(this.$controls)
		if (setting.displaymode.type=="auto"){ //auto slide mode?
			setting.displaymode.pause+=setting.slideduration
			this.maxsteps=setting.displaymode.cycles * this.$imageslides.length
			if (setting.displaymode.pauseonmouseover){
				this.$wrapperdiv.mouseenter(function(){slideshow.ismouseover=true})
				this.$wrapperdiv.mouseleave(function(){slideshow.ismouseover=false})
			}
			this.rotatetimer=setTimeout(function(){slideshow.rotate()}, setting.displaymode.pause)
		}

		var swipeOptions={ // swipe object variables
			triggerOnTouchEnd : true,
			triggerOnTouchLeave : true,
			allowPageScroll: setting.orientation == 'h'? "vertical" : "horizontal",
			swipethreshold: setting.swipethreshold,
			excludedElements:[]
		}

		swipeOptions.swipeStatus = function(event, phase, direction, distance){
			if (phase == 'start' && event.target.tagName == 'A'){ // cancel A action when finger makes contact with element
				evtparent.onclick = function(){
					return false
				}
			}
			if (phase == 'cancel' && event.target.tagName == 'A'){ // if swipe action canceled (so no proper swipe), enable A action
				evtparent.onclick = function(){
					return true
				}
			}
			if (phase == 'end'){
				var navkeyword = /(right)|(down)/i.test(direction)? 'back' : 'forth'
				if ( (setting.orientation == 'h' && /(left)|(right)/i.test(direction)) || (setting.orientation == 'v' && /(up)|(down)/i.test(direction)) )
					slideshow.navigate(navkeyword)
			}
		}

		if (this.$wrapperdiv.swipe){
			this.$wrapperdiv.swipe(swipeOptions)
		}

		this.$wrapperdiv.bind('mouseenter click', function(){
			if (slideshow.$controls && slideshow.$controls.length == 2){
				slideshow.$controls.stop().velocity({opacity: 1})
			}
		})
	
		this.$wrapperdiv.bind('mouseleave', function(){
			if (slideshow.$controls && slideshow.$controls.length == 2){
				slideshow.$controls.stop().velocity({opacity: 0}, 'fast')
			}
		})
	}

}

bgCarousel.routines={

	getSlideHTML:function(setting, imgref, w, h, posprop){
		var posstr=posprop+":"+((posprop=="left")? w : h)
		return '<div class="slide" style="background-image:url(' + imgref[0] + '); position:absolute;'+posstr+';width:'+w+'; height:'+h+';">'
							+ ((imgref[1])? '<div class="desc">' + imgref[1] + '</div>\n' : '')
							+	'</div>'
	},

	getCookie:function(Name){ 
		var re=new RegExp(Name+"=[^;]+", "i"); //construct RE to search for target name/value pair
		if (document.cookie.match(re)) //if cookie found
			return document.cookie.match(re)[0].split("=")[1] //return its value
		return null
	},

	setCookie:function(name, value){
		document.cookie = name+"=" + value + ";path=/"
	},

	createobj:function(){
		var obj={}
		for (var i=0; i<arguments.length; i++){
			obj[arguments[i][0]]=arguments[i][1]
		}
		return obj
	}
}