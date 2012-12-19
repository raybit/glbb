package edu.polynyu.gil.bbpro
{
	import net.flashpunk.debug.Console;	
	import net.flashpunk.Engine;
	import net.flashpunk.FP;
	import net.flashpunk.tweens.motion.Motion;
	
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
		
		public function Main():void 
		{


			super(GCfg.camScreenW *GCfg.sizeRatio , GCfg.camScreenH*GCfg.sizeRatio, 30, false);
			
			sock = new GameSocket( GCfg.localHostStr, GCfg.localSockPort);
			
			FP.world = new MotionWorld_base(sock);

			
		}


		override public function init():void
		{
			trace("FlashPunk has started successfully!");
			if ( this.sock != undefined) {
				this.sock.doConn(); //todo check whether connected
			}
			
			
		}

		//------------------print enhancement ------------------
		private function printJSON(o:Object):void {
			trace("Debug.printJSON");
			trace(parseJSON(o));
		}
		private function parseJSON(o:*, spaces:int = 1):String {
			var str:String = "";
			if(getTypeof(o) == "object") {
				str += "{\n";
				for(var i:* in o) {
					str += getSpaces(spaces) + i + "=";
					if(getTypeof(o[i]) == "object" || getTypeof(o[i]) == "array") {
						str += parseJSON(o[i], spaces + 1) + "\n";
					} else {
						var type:String = getTypeof(o[i]);
						if(type == "string") {
							str += "\"" + o[i] + "\"\n";
						} else if(type == "number") {
							str += o[i] + "\n";
						}
					}
				}
				str += getSpaces(spaces - 1 < 0 ? 0 : spaces - 1) + "}";
			} else if(getTypeof(o) == "array") {
				str += "[";
				var n:int = o.length;
				for(i=0; i<n; i++) {
					str += getSpaces(spaces) + "[" + i + "]=";
					if(getTypeof(o[i]) == "object" || getTypeof(o[i]) == "array") {
						str += parseJSON(o[i], spaces + 1) + "\n";
					} else {
						type = getTypeof(o[i]);
						if(type == "string") {
							str += "\"" + o[i] + "\"";
						} else if(type == "number") {
							str += o[i];
						}
						str += ",";
					}
				}
				str += getSpaces(spaces - 1 < 0 ? 0 : spaces - 1) + "]";
			}
			return str;
		}
		private function getSpaces(n:int):String {
			var str:String = "";
			for(var i:int=0; i<n; i++) {
				str += "  ";
			}
			return str;
		}
		private function getTypeof(o:*):String {
			return typeof(o) == "object" ? (o.length == null ? "object" : "array") : typeof(o);
		}

	

	}

}