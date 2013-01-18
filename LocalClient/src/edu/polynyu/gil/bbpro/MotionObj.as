package edu.polynyu.gil.bbpro 
{
	/**
	 * ...
	 * @author raybit
	 */
	
	import flash.geom.Rectangle;
	public class MotionObj 
	{
		public var id:int;
		
		public var cx:int;
		public var cy:int;
	
		
		public var top:int;
		public var left:int;
		public var rect:Rectangle;
			
		public var w:int;
		public var h:int;
	
		public var psize:int; //size cell's pixels
		public var rsize:int; //size according to w*h& cellsize
		
		public var hp:int;
		public var time:int;
		
		public var preHp:int = 0;
		public var repeatHPCounter:int=0;
		
		private const sizeRatio:uint = 2;
		//private static var camH:int = GCfg.camScreenH;
		private static var camW:int = GCfg.camScreenW;
		
		public function MotionObj(mobjItem:Object) 
		{
			//init this obj by mobItem'
			//mobjItem is a object extracted from socket's json message
			//so it is a internal obj
			
			//Note that: all input x position is the pos in the camera view
			//So, we have to mirror/flip the x postion
			
			//uvLeftX =uvRightX - w
			//motion.x= cvCenterX
			//cvLeftX = cvCenterX -w/2 = camW- uvRightX
			// ?uvLeftx= camW -(cvCenterX-w/2) -w =camW- m.x -w/2
			
			this.w = mobjItem.w;
			this.h = mobjItem.h;
			
			this.cx = mobjItem.x;
			this.cy = mobjItem.y;
			
			
			
			this.id = mobjItem.id;
			this.psize = mobjItem.size;
			this.rsize = mobjItem.r ;//0,1,2
			this.hp = mobjItem.hp;
			this.time = mobjItem.t;
			
			this.top = this.cy - this.h / 2;
			this.left = this.cx -this.w / 2;
			
			this.rect=new Rectangle(
				this.top * sizeRatio,
				this.left * sizeRatio,
				this.w * sizeRatio,
				this.h * sizeRatio
			)
			
		}
		public function refreshData(mobjItem:Object):void {
			this.w = mobjItem.w;
			this.h = mobjItem.h;
			
			this.cx = mobjItem.x;
			this.cy = mobjItem.y;
			
			this.rsize = mobjItem.r ;
			
			//this.id = mobjItem['id'];
			//this.rsize = mobjItem['r'] ;//0,1,2 create at init
			this.psize = mobjItem.size;
			
			this.hp = mobjItem.hp;
			this.time = mobjItem.t;
			
			this.top = this.cy - this.h / 2;
			this.left = this.cx -this.w / 2;
			
			this.rect.top = this.top * sizeRatio;
			this.rect.left = this.left * sizeRatio;
			this.rect.width = this.w * sizeRatio;
			this.rect.height = this.h * sizeRatio;
			
		}
	 
	}

}

