var parser = require("xml2json");
var fs = require("fs");
var sqlite3 = require("sqlite3").verbose();


/**
 * This function will translate the raw xml into a JS object that can be used to generate the C init/runtime command arrays
 * @param {function} callback(translated) - Callback function giving back the JS object containing the prepared JS object
 */
translate = function(callback){
	//TODO: rewrite this, so that an xml string can be passed!
	try{
		var xml=fs.readFileSync("/home/mogyula/devel/dabox/test.xml", "utf8");
		var json = parser.toJson(xml, {arrayNotation:true, object:true}); //Gotta get everything as array, so it'll be easier to walk the JSON tree.
	}catch(err){
		callback(err, null);
		return;
	}
	
	try{
		checkSyntax(json);
	}catch(err){
		callback(err,null);
		return;
	}

	var caller=this;
	var listenerCount=getListenerCount(json);
	var result;
	this.result=[];
	
	//TODO: Throw an error when a trigger was used instead of a listener and vice versa.
	for (var i in json.system[0].device){
		for (var j in json.system[0].device[i].trigger){
			sortArgs(
				json.system[0].device[i].type,
				json.system[0].device[i].trigger[j].name,
				json.system[0].device[i].trigger[j].arg,
				i,j,null,null, //passing these, so the async callback function will get them
				function(trigger_arg_array, i, j, k, l, err){
					
					if (err){
						callback(err, null);
						return;
					}
										
					for (var k in json.system[0].device[i].trigger[j].device){						
						for (var l in json.system[0].device[i].trigger[j].device[k].listener){
							sortArgs(
							json.system[0].device[i].trigger[j].device[k].type,
							json.system[0].device[i].trigger[j].device[k].listener[l].name,
							json.system[0].device[i].trigger[j].device[k].listener[l].arg,
							i,j,k,l,
							function(listener_arg_array, i, j, k, l, err){
								
								if (err){
									callback(err, null);
									return;
								}
								
								getDeviceFunctionID(
								json.system[0].device[i].type,
								json.system[0].device[i].trigger[j].name,
								function(trigger_type_id, trigger_func_id, err){
									
									if(err){
										callback(err,null);
										return;
									}
									
									getDeviceFunctionID(
									json.system[0].device[i].trigger[j].device[k].type,
									json.system[0].device[i].trigger[j].device[k].listener[l].name,
									function(listener_type_id, listener_func_id, err){
										
										if(err){
											callback(err,null);
											return;
										}
										
										var curResult;
										
										curResult=[
											{"trigger":[
												{"device_id":json.system[0].device[i].id},
												{"type_id":trigger_type_id},
												{"func_id":trigger_func_id},
												{"args":trigger_arg_array}
												]
											},
											{"listener":[
												{"device_id":json.system[0].device[i].trigger[j].device[k].id},
												{"type_id":listener_type_id},
												{"func_id":listener_func_id},
												{"args":listener_arg_array}
												]
											}
										]
																				
										caller.result.push(curResult);
										
										if (caller.result.length==listenerCount){
											callback(null, caller.result);
										}
										
										return;
									});
									return;
								});
								return;
							}
							);
						}
					}
					return;
				}
			);
		}
	}
	return;
};
module.exports.translate=translate; //So it can be accessed from other source files.

/**
 * This function will sort the arguments givenen in the  for triggers/listeners in a way, that the actual devices will be able to receive them in the right order at initialisation phase.
 * @param {string} device_type - The name of the device which trigger/listens to the function.
 * @param {string} func_name - The name of the trigger/listener function.
 * @param {string[]} args - The arguments to short.
 * @param {integer} index_i - The "i" index of the loop the caller was in. The function gives this back in the callback, so that the walking of a tree can continue despite async execution.
 * @param {integer} index_j - The "j" index of the loop the caller was in. The function gives this back in the callback, so that the walking of a tree can continue despite async execution.
 * @param {integer} index_k - The "k" index of the loop the caller was in. The function gives this back in the callback, so that the walking of a tree can continue despite async execution.
 * @param {integer} index_l - The "l" index of the loop the caller was in. The function gives this back in the callback, so that the walking of a tree can continue despite async execution.
 * @param {function} callback(arg_array) - Callback function giving back the sorted argument string array.
 */
sortArgs = function(device_type, func_name, args, index_i, index_j, index_k, index_l, callback){
	
	if(!args){
		callback([""], index_i, index_j, index_k, index_l); //Return this if no arguments were given.
		return;
	}
	
	var _db = new sqlite3.Database("/home/mogyula/devel/dabox/id.db",sqlite3.OPEN_READONLY); //Open our database.
			
	_db.all("SELECT"+
	" type_id.name AS type_name,"+
	" func_id.arg_cnt AS arg_cnt,"+
	" func_id.name AS func_name,"+
	" arg_order.arg_no AS arg_no,"+
	" arg_order.arg_name AS arg_name"+
	" FROM type_id INNER JOIN func_id"+
	" ON type_id.type_id=func_id.type_id"+
	" INNER JOIN arg_order"+
	" ON type_id.type_id=arg_order.type_id"+
	" AND func_id.func_id=arg_order.func_id"+
	" WHERE type_name='"+device_type+"' AND"+
	" func_name='"+func_name+"'"
	,function(err, row){
		
		if(err){
			callback(null, null, null, null, null, err);
			return;
		}
		
		//TODO: error handling
		//create an array with length arg_cnt, if it doesn't exist yet
		var	_arg_array = new Array(row[0].arg_cnt);
		
		//Let's search for that attribute amongst the given ones...
		for (var i in args){
			for (var j in row){
				if (args[i].name==row[j].arg_name){
					//...and put it in this array in order.
					_arg_array[--row[j].arg_no] = args[i].$t;
				}
			}
		}
		callback(_arg_array, index_i, index_j, index_k, index_l, null);
		return;
	});
	_db.close();
	return;
}

getDeviceFunctionID = function(deviceName, functionName, callback){
	var _db = new sqlite3.Database("/home/mogyula/devel/dabox/id.db",sqlite3.OPEN_READONLY);
	
	_db.each("SELECT type_id.type_id AS type_id, func_id.func_id AS func_id"+
	" FROM type_id INNER JOIN func_id"+
	" ON type_id.type_id=func_id.type_id"+
	" WHERE type_id.name='"+deviceName+"'"+
	" AND func_id.name='"+functionName+"'"
	,function(err, row){
		
		if (err){
			callback(null, null, err);
			return;
		}
		
		callback(row.type_id, row.func_id, null);
		return;
	});
	_db.close();
	return;
}

/**
 * This function counts the <listener> elements in the XML tree, so that the total number of trigger-listener pairs can be known.
 * @param {object} obj - The JS object containing the parsed XMl tree
 */
getListenerCount = function(obj){
	var _listenerCount=0;
	
	for (var i in obj.system[0].device){
		for (var j in obj.system[0].device[i].trigger){
			for (var k in obj.system[0].device[i].trigger[j].device){
					_listenerCount+=obj.system[0].device[i].trigger[j].device[k].listener.length;
			}
		}
	}
	return _listenerCount;
}

/**
 * This function checks the semantics of the JS object parsed from the initial XML
 * @param {object} obj - The JS object containing the parsed XML tree
 */
checkSyntax = function(obj){
	var errorMsg="Error while translating XML: " //every error message will start with this
	var children; //just a loop counter

//TODO: check everywhere, that the given number of args were given
	
	//only one <system> can and should exist.
	if (Object.keys(obj).length!=1 || Object.keys(obj)[0]!="system"){
		throw errorMsg+"only a single <system>...</system> element should exist at the top level!\n   "+
		"In: system";
	}
	
	//only <device> element(s) should be in the <system>
	var system_keys = Object.keys(obj.system[0]);
	for(children in system_keys){
		if (system_keys[children]!="device"){
			throw errorMsg+"the <system> element should only contain one or more <device> elements!\n   "+
			"In: system";
		}
	}
	
	//iterating outer <device> elements...
	for (var i in obj.system[0].device){
		
		//only <device type=... id=...> should exist.
		var outer_device_attributes=getAttributes(obj.system[0].device[i]);
		if (outer_device_attributes.length!=2 ||
			outer_device_attributes.indexOf("type") == -1 ||
			outer_device_attributes.indexOf("id") == -1){
			throw errorMsg+"the <device> elements must have one \"type\", and one \"id\" property defined!\n   "+
			"In: system > device("+obj.system[0].device[i].type+")\n";
		}
		
		//Members of outer <device>s must be <trigger>s
		var outer_device_keys = Object.keys(obj.system[0].device[i]);
		for(children=2; children<outer_device_keys.length; children++){ //the 0 and 1 index was the "type" and "id" attributes.
			if (outer_device_keys[children]!="trigger"){
				throw errorMsg+"the outer <device> element should only contain one or more <trigger> elements!\n\   "+
				"In: system > device("+obj.system[0].device[i].type+")\n";
			}
		}
		
		//iterating through <trigger>s...
		for (var j in obj.system[0].device[i].trigger){
			
			var trigger_attributes = getAttributes(obj.system[0].device[i].trigger[j]);
			if (trigger_attributes.length != 1 ||
				trigger_attributes.indexOf("name") == -1){
				throw errorMsg+"the <trigger> element should have one \"name\" property defined!\n   "+
				"In: system > device("+obj.system[0].device[i].type+")\n";
			}
			
			//iterating through trigger <arg>s and <device>s inside <trigger>s
			var trigger_keys = Object.keys(obj.system[0].device[i].trigger[j]);
			for(children=1 ;children<trigger_keys.length;children++){
				
				//in case no device to listen was given
				if(trigger_keys.indexOf("device")==0){
					throw errorMsg+"the <trigger> element should contain at least one <device> element!\n   "+
					"In: system > device("+obj.system[0].device[i].type+") > "+
					"trigger("+obj.system[0].device[i].trigger[j].name+")\n";
				}
				
				//in case anything else than <arg> or <device> was inside the <trigger> element
				if (trigger_keys[children]!="arg" &&
					trigger_keys[children]!="device"){
					throw errorMsg+"the <trigger> element should only contain <arg> and <device> elements!\n   "+
					"In: system > device("+obj.system[0].device[i].type+") > "+
					"trigger("+obj.system[0].device[i].trigger[j].name+")\n";
				}
			}
			
			//looping through the <arg> elements to see if they only have a name attribute and and a value inside
			for (children in obj.system[0].device[i].trigger[j].arg){
				
				var trigger_arg_attributes=getAttributes(obj.system[0].device[i].trigger[j].arg[children]);
				//args should have a name
				if (trigger_arg_attributes[0]!="name"){
					throw errorMsg+"the <arg> elements must have a \"name\" property defined!\n   "+
					"In: system > device("+obj.system[0].device[i].type+") > "+
					"trigger("+obj.system[0].device[i].trigger[j].name+")\n";
				}
				//args should have a value
				if (trigger_arg_attributes[1]!="$t"){
					throw errorMsg+"the <arg> elements must have a defined value!\n   "+
					"In: system > device("+obj.system[0].device[i].type+") > "+
					"trigger("+obj.system[0].device[i].trigger[j].name+") > "+
					"arg("+obj.system[0].device[i].trigger[j].arg[children].name+")\n";
				}
			}
			
			//looping through the inner <device>s
			for (var k in obj.system[0].device[i].trigger[j].device){
				
				//check if only the "type" and "id" attributes were given to the inner <device> element
				var inner_device_attributes = getAttributes(obj.system[0].device[i].trigger[j].device[k]);
				if (inner_device_attributes.length != 2 ||
					inner_device_attributes.indexOf("type")==-1 ||
					inner_device_attributes.indexOf("id")==-1){
					throw errorMsg+"the <device> elements must have one \"type\", and one \"id\" property defined!\n   "+
					"In: system > device("+obj.system[0].device[i].type+") > "+
					"trigger("+obj.system[0].device[i].trigger[j].name+")\n"
				}
				
				var inner_device_keys=Object.keys(obj.system[0].device[i].trigger[j].device[k]);
				for(children=2; children<inner_device_keys.length;children++){
					if(inner_device_keys[children]!="listener"){
						throw errorMsg+"the inner <device> element should only contain <listener> elements\n   "+
						"In: system > device("+obj.system[0].device[i].type+") > "+
						"trigger("+obj.system[0].device[i].trigger[j].name+") > "+
						"device("+obj.system[0].device[i].trigger[j].device[k].type+")\n";
					}
				}
				
				//looping through the <listener> elements
				for (var l in obj.system[0].device[i].trigger[j].device[k].listener){
					
					//checking that the listener element has only one attribute, which is "name"
					var listener_attributes=getAttributes(obj.system[0].device[i].trigger[j].device[k].listener[l]);
					if (listener_attributes.length!=1 ||
						listener_attributes.indexOf("name")==-1){
						throw "the <listener> element should have one \"name\" property defined!\n   "+
						"In: system > device("+obj.system[0].device[i].type+") > "+
						"trigger("+obj.system[0].device[i].trigger[j].name+") > "+
						"device("+obj.system[0].device[i].trigger[j].device[k].type+") > "+
						"listener("+obj.system[0].device[i].trigger[j].device[k].listener[l].name+")\n";
					}
					
					//checking that only <arg>s are in <listener>s
					var inner_device_keys=Object.keys(obj.system[0].device[i].trigger[j].device[k].listener[l]);
					for(children=1; children<inner_device_keys.length; children++){
						if(inner_device_keys[children]!="arg"){
							throw "the <listener> element should only contain <arg> elements!\n   "+
							"In: system > device("+obj.system[0].device[i].type+") > "+
							"trigger("+obj.system[0].device[i].trigger[j].name+") > "+
							"device("+obj.system[0].device[i].trigger[j].device[k].type+") > "+
							"listener("+obj.system[0].device[i].trigger[j].device[k].listener[l].name+")\n";
						}
					}
					
					//looping through <arg>s of listeners
					for (children in obj.system[0].device[i].trigger[j].device[k].listener[l].arg){
						
						var listener_arg_attributes = getAttributes(obj.system[0].device[i].trigger[j].device[k].listener[l].arg[children]);
						
						//checking if they all have a "name" attribute
						if (listener_arg_attributes[0]!="name"){
							throw errorMsg+"the <arg> elements must have a \"name\" property defined!\n   "+
							"In: system > device("+obj.system[0].device[i].type+") > "+
							"trigger("+obj.system[0].device[i].trigger[j].name+") > "+
							"device("+obj.system[0].device[i].trigger[j].device[k].type+") > "+
							"listener("+obj.system[0].device[i].trigger[j].device[k].listener[l].name+")\n";
						}
				
						//and a value
						if (listener_arg_attributes[1]!="$t"){
							throw errorMsg+"the <arg> elements must have a defined value!\n   "+
							"system > device("+obj.system[0].device[i].type+") > "+
							"trigger("+obj.system[0].device[i].trigger[j].name+") > "+
							"device("+obj.system[0].device[i].trigger[j].device[k].type+") > "+
							"listener("+obj.system[0].device[i].trigger[j].device[k].listener[l].name+") > "+
							"arg("+obj.system[0].device[i].trigger[j].device[k].listener[l].arg[children].name+")\n";
						}
					}
				}
			}
		}
	}
	return; //if there was no error
}

/**
 * This function returns an array of those top-level elements that have no children in the object.
 * This corresponds to the attributes and values of elements (not sub-elements) of the XML tree.
 * @param {object} obj - A JS object
 */
getAttributes = function(obj){
	var result = [];

	for (var label in obj){
		if(typeof(obj[label])=="string"){
			result.push(label);
		}
	}
	return result;
}
