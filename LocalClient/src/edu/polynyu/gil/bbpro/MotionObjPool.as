package edu.polynyu.gil.bbpro 
{
	import flash.utils.Dictionary;
	/**
	 * ...
	 * @author raybit
	 * this class reads the motionlist(array) from stabilizer(python)
	 * each motionObj 
	 *       			{'id':mobj['oid'],
                         'x':mobj['xPos'],
                         'y':mobj['yPos'],
                         'size':mobj['cellSize'],
                         'op':mobj['op'],
                         'h':mobj['height'],
                         'w':mobj['width'],
                         'r':mobj['range'], #range:0-s,1-m,2-l
                         't':mobj['lifeTimer'],  #time:
						  'hp':mobj['HP']  #time:
                         }  
						 
	 */

		
	public class MotionObjPool 
	{
		private var opSet:Object = {
				create:"create",
				update:"update",
				del:"del"
		};
			
		public var objDict:Dictionary = new Dictionary();
		public var objCounter:int = 0;
		
		public function MotionObjPool() 
		{
			
		}
		public function getDict():Dictionary {
			return this.objDict;
		}
		public function update(motionObjList:Array):void {
			//trace('update mobj-------');
			var mlen = motionObjList.length;
			if ( mlen == 0) {
				//skip
				return;
			}
			var i:int = 0;
			var item:Object
			var id:int = 0;
			var op:String;
			var mobj:MotionObj;
			
			for ( ; i < mlen; i++) {
				var item:Object = motionObjList[i];
				id = item.id;
				
								
				op = item.op;
				switch(op) {
					case opSet.create:
						mobj = new MotionObj(item);
						this.objCounter++;
						this.objDict[id] = mobj;
						//trace('create mobj:' + id);
						break;
					case opSet.del:
						mobj = this.objDict[id];
						if (mobj == undefined || mobj == null) {
							//skip
							//trace('Warnning: fail to del mobj:'+id);
						}else {
							delete this.objDict[id];
							this.objCounter--;
							trace('del:mobj:'+id +',hp:'+mobj.hp+'    lenOfDict:'+this.objCounter);
						
						}
						break;
						
					default: // opSet.update
						mobj = this.objDict[id];
						if (mobj == undefined || mobj == null) {
							trace('faked create mobj:' + id);
							mobj = new MotionObj(item);
							this.objCounter++;
							this.objDict[id] = mobj;
						}else {
							//trace('update mobj:' + id+',item-hp:'+item.hp);
							mobj.refreshData(item);
							//trace('mobj hp:' + mobj.hp);
						}
					
				}
			} 
		}
			
	}

}