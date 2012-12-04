package {

//--flashpuck
    import net.flashpunk.debug.Console;	
	import net.flashpunk.Engine;
	import net.flashpunk.FP;
	import src.MainMenu;
	
    import flash.display.MovieClip;
    import flash.events.MouseEvent;
    import flash.utils.ByteArray;
    import flash.events.ProgressEvent;
  
  


//  import com.adobe.serialization.json.JSONObject
    public class Main extends Engine{
  

  	private var sock:GameSocket;
  	private var mCanvas:MotionCanvas;

	
	
	
    public function Main(  ) {
		super(1280, 960, 30, false);
		FP.world = new MainMenu;
		
		
      // Connect to the server
	  /*
		sock = new GameSocket( "127.0.0.1", 2901 );
      
		mCanvas = new MotionCanvas(1280,960);	  
		this.stage.addChild(mCanvas.canvas);
		  
		this.stage.addChild(new BasicInfo());
		 
		sock.addEventListener( SocketEvent.ON_Recv_Data, onSockRecvData ); //sock will dispatch the event itself
		//auto call init(); 
		*/
	}
	override public function init():void
	{
		trace("FlashPunk has started successfully!");
		//this.sock.doConn(); //todo check whether connected
	}
		
/*
	private function onEnterFrame():void{
		//int byteVal= Math.floor(Math.random()*(16));//0-15
		
	}
	*/
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
		 	 this.mCanvas.drawMotion(event.dataObj["bg"]); //:Array
		 }else{
		 	//private autoUpdate msg from localServer's stabilizer

		 }
   		
		

   	}

   	//not use now
	public function onClick(ev:MouseEvent):void  
	{  /*
			if(this.isConnection)  
			{  
					var mes:String="flash"+Math.floor(Math.random()*1000000);  
					  
					this.sendMes(mes);  
					  
					trace(mes);  
					  
			}else{  
					trace("服务未被连接!");  
			}  
		*/
	}
	


	
	
	//------------------print enhancement ------------------
	function printJSON(o:Object):void {
		trace("Debug.printJSON");
		trace(parseJSON(o));
	}
	function parseJSON(o:*, spaces:int = 1):String {
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
	function getSpaces(n:int):String {
		var str:String = "";
		for(var i:int=0; i<n; i++) {
			str += "  ";
		}
		return str;
	}
	function getTypeof(o:*):String {
		return typeof(o) == "object" ? (o.length == null ? "object" : "array") : typeof(o);
	}


  }
}