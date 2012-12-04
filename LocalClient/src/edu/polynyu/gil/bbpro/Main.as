package edu.polynyu.gil.bbpro
{
	import net.flashpunk.debug.Console;	
	import net.flashpunk.Engine;
	import net.flashpunk.FP;
	
	import flash.display.Sprite;
	import flash.events.Event;

	/**
	 * ...
	 * @author raybit
	 */
	[Frame(factoryClass="edu.polynyu.gil.bbpro.Preloader")]
	public class Main extends Engine 
	{
		private var sock:GameSocket;
		private var motionBM:MotionBitMap=new MotionBitMap(1280,960);
		
		public function Main():void 
		{
			super(1280, 960, 30, false);
			FP.world = new MWorld(motionBM);
			
			sock = new GameSocket( "127.0.0.1", 2901 );
			sock.addEventListener( SocketEvent.ON_Recv_Data, onSockRecvData ); //sock will dispatch the event itself
			
			//if (stage) init();
			//else addEventListener(Event.ADDED_TO_STAGE, init);
		}


		override public function init():void
		{
			trace("FlashPunk has started successfully!");
			this.sock.doConn(); //todo check whether connected
		}
		private function onSockRecvData (event:SocketEvent):void{

			trace('in onsock recvdata');
			 
			 //trace('len of dataArr ?=3? :'+event.dataArr.length);

			 //recvDataArr Format:
			 //
			 //["ft"] format info
			 //["ml"] motionRectList
			 //["bg"] imgMartix

			var formatType:int = int(event.dataObj["ft"]);

			if (formatType==0){
				//main msg from motion progran
				this.motionBM.update(event.dataObj["bg"]); //:Array
			}else{
				//private autoUpdate msg from localServer's stabilizer

			}

			

		}
	}

}