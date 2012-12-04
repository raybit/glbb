package edu.polynyu.gil.bbpro 
{
	import flash.geom.Point;
	import net.flashpunk.Entity;
	import net.flashpunk.graphics.Canvas;
	import net.flashpunk.World;
	//import src.MotionBgEngity;
	
	/**
	 * ...
	 * @author raybit
	 */
	public class MWorld extends World 
	{
		private var motionBitmap:MotionBitMap;
		private var mBg:Canvas;
		private var mBgEntity:Entity;
		public function MWorld(mBitMap:MotionBitMap) 
		{
			this.motionBitmap = mBitMap;

			mBg = new Canvas(1280,960);
			this.addGraphic(mBg);// Entity);
		}
		override public function render():void {
			
			//mBgEntity.renderTarget = this.motionBitmap.getBitMapData();
			mBg.draw(0,0,this.motionBitmap.getBitMapData());
			//_graphic.render(
			super.render();
		
		}
	}

}