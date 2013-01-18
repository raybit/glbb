package edu.polynyu.gil.bbpro 
{
	/**
	 * ...
	 * @author raybit
	 */
	import flash.display.BitmapData;
	import flash.geom.Point;
	import flash.geom.Rectangle;
	import flash.utils.Dictionary;
	
	import net.flashpunk.graphics.Canvas;
	import net.flashpunk.graphics.Image;
	import net.flashpunk.Entity;
	

	//import mc_tween2
	import flash.display.BitmapData;
	import flash.geom.*;
	import flash.filters.*;


	public class MotionWorld_base extends World_base 
	{
		
		private var _mBitMap:MotionBitMap;
		private var _mObjPool:MotionObjPool = new MotionObjPool();
		
		private var _mBgCanvas:Canvas;
		private var _mObjCanvas:Canvas;
		
		//private var _mBgEntity:Entity;
		
		private const sizeRatio:uint = 2;
		private const origW:uint = 640;
		private const origH:uint = 480;
		
		private const mObjCol0:uint = 0x00CC00;
		private const mObjCol1:uint = 0xCC0000;
		private const mObjCol2:uint = 0x0000CC;
		
		private const mObjColMaxAlpha:Number = 0.5;
		
		private const emptyData:BitmapData= new BitmapData(origW*sizeRatio,origH*sizeRatio,true,0);
		private const bgRect:Rectangle = new Rectangle(0, 0, origW * sizeRatio, origH * sizeRatio);
		
		private const localDebug:Boolean = true;

		//-----------for drawing begin
		/*
		[Embed(source = '/assets/plus.gif')] private const PLUS_img:Class;
		private var target:Entity = new Entity(0, 0, PLUS_img);		
		
		private var lineDisplay_Canvas:Canvas; //lineDisplay_mc
		private var lineDisplay_mc:Entity = new Entity(0, 0, lineDisplay_Canvas);
		*/
		//-----------for drawing end

		public function MotionWorld_base(sock:GameSocket) 
		{
			super(sock);
			
			if (!this.localDebug) {
				this._mObjPool = new MotionObjPool();
				
				//_mBitMap is pixels source 
				this._mBitMap = new MotionBitMap(origW * sizeRatio, origH * sizeRatio);
				
				//_mBgCanvas is used to draw _mBitMap data on one layer
				this._mBgCanvas = new Canvas(origW*sizeRatio,origH*sizeRatio);
				this._mBgCanvas.blend = flash.display.BlendMode.MULTIPLY;
				
				//_mObjCanvas is for drawing "focused interesting point" on one layer
				this._mObjCanvas  =new Canvas(origW*sizeRatio,origH*sizeRatio);

				
				this.addGraphic(this._mObjCanvas,1); 
				this.addGraphic(this._mBgCanvas, 2); 
			}
			this.addGraphic(new Image(Assets.BG_dog),3); 
			
			
		}
	

		
		override public function render():void {
			
			if (!localDebug) {
				//do the drawing stuff
				//01 draw the dynamic region on mBGCanvas and this canvas will overlay on other pic
				this._mBgCanvas.erase(this._mBitMap.getBitMapData().rect);
				this._mBgCanvas.draw(0,0,this._mBitMap.getBitMapData());
				
				var dict:Dictionary = this._mObjPool.getDict();
				
				
				//02 clear and redraw the obj-canvass
				this._mObjCanvas.erase(bgRect);
				for each (var mObj:MotionObj in dict) {
					if (mObj.hp <= -27) {
						delete dict[mObj.id];
						this._mObjPool.objCounter--;
						trace('word del:mobj:'+mObj.id +',hp:'+mObj.hp+'    lenOfDict:'+this._mObjPool.objCounter);
						continue;
					}
					if (mObj.hp < 100 && mObj.hp == mObj.preHp) {
						
						mObj.repeatHPCounter++;
						
						if (mObj.repeatHPCounter > 60) {
							delete dict[mObj.id];
							this._mObjPool.objCounter--;
							trace('word del:mobj:'+mObj.id +',hp:'+mObj.hp+'    lenOfDict:'+this._mObjPool.objCounter);
							continue;
						}
					}else {
						mObj.preHp = mObj.hp;
					}
						
					trace('mobj id:' + mObj.id + ', hp:' + mObj.hp+" rsize:"+mObj.rsize);
					
					if(mObj.rsize==0 && mObj.hp>250 ){
						this._mObjCanvas.drawRect(mObj.rect, mObjCol0,0.15+0.8*(mObj.hp/1000));//
					}
					/*
					 else if (mObj.rsize == 1) {
						//this._mObjCanvas.drawRect(mObj.rect, mObjCol1,  mObj.hp / 100);
					}else {
						//this._mObjCanvas.drawRect(mObj.rect, mObjCol2,  mObj.hp / 100);	
					}
					*/
				}
				
			}
			
		
			super.render();
			//trace('......in render');
		
		}
		
		override public function onSockRecvData (event:SocketEvent):void {
			//trace('test onSockRecvData mworld');
			
			 //recvDataArr Format:
			 //
			 //["ft"] format info
			 //["ml"] motionRectList
			 //["bg"] imgMartix
			if (!localDebug) {
				var formatType:int = int(event.dataObj["ft"]);

				if (formatType==0){
					//main msg from motion progran
					this._mBitMap.update(event.dataObj["bg"]); //:Array
					this._mObjPool.update(event.dataObj["ml"]);
					//printJSON(event.dataObj["ml"]);
				}else if(formatType==1 ) {
					//private autoUpdate msg from localServer's stabilizer
					this._mObjPool.update(event.dataObj["ml"]);
				}
			}
		}
	}


}

