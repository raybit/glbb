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
	public class World_base extends World 
	{



		public var sock:GameSocket;
		
		public function World_base(sock:GameSocket) 
		{
			this.sock = sock;
			this.sock.addEventListener( SocketEvent.ON_Recv_Data, onSockRecvData ); //sock will dispatch the event itself
		}
		public function onSockRecvData (event:SocketEvent):void {
			trace('test onSockRecvData mworld');
		}
		

	}

}