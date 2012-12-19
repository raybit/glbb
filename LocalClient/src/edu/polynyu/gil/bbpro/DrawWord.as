package edu.polynyu.gil.bbpro 
{
	import net.flashpunk.Entity;
	import net.flashpunk.graphics.Canvas;
	import net.flashpunk.World;
	
	//---merge draw
	import flash.display.BitmapData;
	import flash.geom.*;
	import flash.filters.*;

	/**
	 * ...
	 * @author raybit
	 */
	public class DrawWord extends World 
	{
		public var drawTarget:Entity; 
		public var drawing:Entity; 
		
		private var lineDisplayBmpData:BitmapData = new BitmapData(990, 590, true, 0x000000FF);
		private var lineDisplayCanvas:Canvas = new Canvas(990, 590);
		// Setup some constants
		private var colorF:ColorMatrixFilter = new ColorMatrixFilter([
														 1.1,0,0,0,0,
														 0,.99,0,0,0,
														 0,0,.99,0,0,
														 0,0,0,.999,0
														 ]);
													 
		private var blurF:BlurFilter = new BlurFilter(4,4,3);
		private var rect:Rectangle = new Rectangle(0, 0, 990, 590);
		private var pt:Point = new Point(0, 0);

		public function DrawWord() 
		{
			addGraphic(Assets.BG_img,0);
			addGraphic(lineDisplayCanvas,1);
			
			drawTarget = new Entity(0, 0, Assets.plus);
			drawTarget.layer = 2;
			
			add(drawTarget);
			 
			drawing = new Entity();
			
			
			this.createEmptyMovieClip("mcDrawing",this.getNextHighestDepth());

			mcDrawing._visible = false;
			mcDrawing.clear();
			mcDrawing.moveTo(target._x, target._y);

		}
		
	}

}





//var target:MovieClip = mcPlus;

// Setup bitmapData for blitting drawing lines into


//this.createEmptyMovieClip("lineDisplay_mc",this.getNextHighestDepth());
//lineDisplay_mc.attachBitmap(lineDisplayBmpData,1);

// Setup some constants
/*
var colorF:ColorMatrixFilter = new ColorMatrixFilter([
													 1.1,0,0,0,0,
													 0,.99,0,0,0,
													 0,0,.99,0,0,
													 0,0,0,.999,0
													 ]);

var blurF:BlurFilter = new BlurFilter();
blurF.blurX = 4;
blurF.blurY = 4;
blurF.quality = 3;

var rect:Rectangle = new Rectangle(0, 0, Stage.width, Stage.height);
var pt:Point = new Point(0, 0);
*/
// ******************************** Pen functions ******************************** 
this.createEmptyMovieClip("mcDrawing",this.getNextHighestDepth());

mcDrawing._visible = false;
mcDrawing.clear();
mcDrawing.moveTo(target._x,target._y);

function MovePen() {
	var nX:Number = Math.random() * 1024 - 50;
	var nY:Number = Math.random() * 650 - 50;

	var pt1:Point = new Point(target._x, target._y);
	var pt2:Point = new Point(nX, nY);

	var cPt:Point = new Point(Math.random() * 990, Math.random() * 550);

	target.bezierSlideTo(cPt.x,cPt.y,pt2.x,pt2.y,1,"easeInOutSine",0,MovePen);

}

// Move the pen around the screen
MovePen();

// ******************************** Drawing functions ******************************** 
var thickMin:Number = 5;
var thickMax:Number = 50;
var thickness:Number = thickMin;
var dir:String = "up";
var targetLast:Point = new Point(target._x,target._y);
var count:Number = 0;

this.onEnterFrame = function() {
	if (thickness < thickMax && dir == "up") {
		thickness += .5;
	} else {
		dir = "down";
	}
	if (thickness > thickMin && dir == "down") {
		thickness -= .5;
	} else {
		dir = "up";
	}
	
	mcDrawing.clear();
	mcDrawing.moveTo(targetLast.x,targetLast.y);
	mcDrawing.lineStyle(thickness,0x000000,100); // 0xAABBCC
	mcDrawing.lineTo(target._x,target._y);

	
	if (count % 45 == 0) {
		var splatScale:Number = Math.random()*300+25;
		mcDrawing.attachMovie("splat_id","splat",this.getNextHighestDepth(),{_x:target._x, 
																			 _y:target._y,
																			 _xscale:splatScale,
																			 _yscale:splatScale,
																			 _rotation:Math.random()*360});
		mcDrawing.splat.gotoAndStop(Math.ceil(Math.random()*3));
	}
	
	
	targetLast.x = target._x;
	targetLast.y = target._y;
	
	// Blit
	lineDisplayBmpData.lock();
	if (count % 5 == 0) {
		lineDisplayBmpData.applyFilter(lineDisplayBmpData, rect, pt, colorF);
		lineDisplayBmpData.applyFilter(lineDisplayBmpData, rect, pt, blurF);
	}
	//lineDisplayBmpData.draw(mcDrawing,new Matrix(),new ColorTransform(),"hardlight");
	lineDisplayBmpData.draw(mcDrawing);
	lineDisplayBmpData.scroll(Math.random()*2,Math.random()*2);
	lineDisplayBmpData.unlock();
	
	removeMovieClip(mcDrawing.splat);
	
	count++;
};