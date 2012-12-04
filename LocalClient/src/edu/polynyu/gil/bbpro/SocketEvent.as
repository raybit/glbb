package edu.polynyu.gil.bbpro
{
     import flash.events.Event;
     public class SocketEvent extends Event
     {
         
          public static const ON_Recv_Data:String = "onRecvData";
        
          public static const ON_Send_Data:String = "onSendData";

          /*customMessage is the property will contain the message for each event type dispatched */
          public var customMessage:String = "";
          public var dataObj:Object ;
          public function SocketEvent(type:String, bubbles:Boolean=false, cancelable:Boolean=false):void
          {
               //we call the super class Event
               super(type, bubbles, cancelable);
          }
     }
}