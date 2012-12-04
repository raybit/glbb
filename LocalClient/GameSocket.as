package  {
	import flash.net.Socket;
	import flash.utils.ByteArray;
  	import flash.events.*;

	import com.adobe.serialization.json.JSON;
	
	public class GameSocket extends EventDispatcher {
		
    	private var socket:Socket;
		private var isConnection:Boolean=false;
		private var reads:ByteArray;
	
		private var sEvt:SocketEvent;
		private var _host:String;
		private var _port:int;
		
		public function GameSocket(host:String,port:int) {
			// constructor code
			_host= host;
			_port =port;
			init();
		}
		private function init():void{
		  socket = new Socket(  );
		
		  // Add an event listener to be notified when the connection
		  socket.addEventListener( Event.CONNECT, onConnect );
		  socket.addEventListener(ProgressEvent.SOCKET_DATA,onRecvData);
		  
		}
		public function doConn():void{
			socket.connect( _host, _port );
			
		}
		private function onConnect( event:Event ):void {
      		trace( "The socket is now connected..." );
			this.isConnection=true;
		  
	
		}
		
		//NOT USE, need design API b4 using
		public function sendMes(mes:String):void  
		{  
			var bytes:ByteArray=new ByteArray();  
			  
			bytes.writeUTFBytes(mes+"\n");  
			  
			bytes.position=0;  
			  
			socket.writeBytes(bytes);  
			  
			socket.flush();  
				  
		}  

		public function onRecvData(ev:ProgressEvent):void  
		{  
				
			var nextPackegLen:int=0; 
			if(socket.bytesAvailable)  
			{  
					reads=new ByteArray();  
					socket.readBytes(reads);//,reads.position,nextPackegLen);  
					 
					//trace("recv-data msgLen:" + reads.length);  
					//trace(reads.toString());
					try{
						//when we recv more than one packet, we only process the first one and ignore others
						sEvt = new SocketEvent("onRecvData");
						sEvt.dataObj = new Object();
						sEvt.dataObj = JSON.decode(reads.toString().split("\n")[0]);
						

						dispatchEvent(sEvt);
						  //drawMotion(jsonResponse); //interface 

					}catch(error:Error){
						trace('error in input strem');
						trace(reads.toString())
					}
					
			}  
		}  


	
	}


	
}
