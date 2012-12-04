package  edu.polynyu.gil.bbpro 
{
	import net.flashpunk.Entity;
	
     import flash.events.Event;
     import flash.display.BitmapData;
     import flash.display.Bitmap;

     import flash.geom.Rectangle;
  




     public class MotionBitMap 
     {
		//public var canvas:Bitmap;

		private var _output : BitmapData;
	
		//these three var need fit to imcoming motionmap scale and its structure
		private var _fixedW:int =640;
		private var _fixedH:int =480; 
		private var _fixedCellSize:int=5;
	      
          //private var _W:int;//= _fixedW/ _fixedCellSize;	 
		//private var _H:int;//= _fixedH/ _fixedCellSize;

		private var _cellSizeW:Number;
		private var _cellSizeH:Number;

		private var fgCol:uint = 0xFF0000;
		private var bgCol:uint = 0x000000;
	 
		public function MotionBitMap(w:int=640,h:int=480){

			/*
				we can stretch the canvas from originial fixed camView size(640*480) to any size we want.
				It is achieved by redefining the shape of cell(the atmoic drawable area). So 

			*/
               var col:uint = 0x000000; //24bit col

               var wRatio:Number = w/_fixedW;
               var hRatio:Number = h/_fixedH;


               _cellSizeW = wRatio * _fixedCellSize;
               _cellSizeH = hRatio * _fixedCellSize;


               _output = new BitmapData(w, h, false, col);
              // canvas = new Bitmap(_output);

         }
		
		public function getBitMapData():BitmapData {
			return this._output;
		}
		//update the bitmap data
		public function update(motionMap:Array):void{
          /*
		motion map is a compressed (128)*96 martix
		each point stand for a 5*5 block
		so totoal size is 640*480
		we dont save all the pixels of one line, but combine the pixels of the same color.
		FE: 0-while,1-black
		   one line is 00001110000011
		   that line would be [0,4,3,5,2], 0(white)*4+(black)*3+(white)*5+(black)*2
		
		motionMap is a json, 2D array, we get it from server socket
		*/
		//The error( Cannot access a property or method of a null object reference) may caused by wrong [W,H] boundry between outside motionMap and internal setting
		//

			_output.lock();
			var rect:Rectangle;
			var xx,yy,maxY,drawPosX,drawPosY,sizeW,sizeH,rowLen:int;
			var subArr:Array;

			drawPosX=0;
			drawPosY=0;

			sizeH=_cellSizeH;
			sizeW=0;
			var c1:uint = fgCol;
			var c0:uint = bgCol;
			var maxY=_fixedH/_fixedCellSize;

			var isBlack:Boolean;//false;
			for(yy=0;yy<maxY;yy++){
				//subArr is the level-2 array, its length is dynamic.
				subArr = (motionMap[yy] as Array)
				rowLen = subArr.length;

				//reset draw X-header to 0
				drawPosX =0;

				//cut the first elem as the begin color

			
				isBlack =subArr[0]==1?true:false;
					
				for(xx=1;xx< rowLen;xx++){ 
					//juduge draw region
					sizeW=subArr[xx]*_cellSizeW;                    
					rect= new Rectangle(drawPosX, drawPosY, sizeW, sizeH);

					if(isBlack){
						 //black, draw fgCol
						 _output.fillRect(rect, c1)
						 
					}else{
						//white, draw bgCol
						 _output.fillRect(rect, c0)
						                   
						 
					} 
					isBlack= !isBlack;
					//move X-header 
					drawPosX+=sizeW;
				}
				//increase draw Y-header by cell's H
				drawPosY+=_cellSizeH;         
				

				/*
				for(xx=0;xx< rowLen;xx+=2){ 
					//juduge draw region
					sizeW=subArr[xx+1]*_cellSizeW;                    
					rect= new Rectangle(drawPosX, drawPosY, sizeW, sizeH);

					if(subArr[xx]==0){
						 //white, draw bgCol
						 _output.fillRect(rect, c0)
					}else{
						 //white, draw fgCol
						 _output.fillRect(rect, c1)                   
						 
					} 

					//move X-header 
					drawPosX+=sizeW;
				}
				//increase draw Y-header by cell's H
				drawPosY+=_cellSizeH;         
				*/
			}
			_output.unlock();

			trace('doing draw something')
		  
		}
	 }
}