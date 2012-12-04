package edu.polynyu.gil.bbpro 
{
	import net.flashpunk.Entity;
	import net.flashpunk.graphics.Image;
	
	/**
	 * ...
	 * @author raybit
	 */
	public class TestEngity extends Entity 
	{
		[Embed(source = '/assets/player.png')] private const PLAYER:Class;
		public function TestEngity() 
		{
			graphic = new Image(PLAYER);
		}
		override public function update():void
		{

			trace("MyEntity updates.");

		}
	}

}