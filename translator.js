var parser = require("xml2json");
var fs = require("fs");
var sqlite3 = require("sqlite3").verbose();

/**
 * This function will translate the raw xml into blocks of C initialisation code that will be built into the actual target binary.
 * @param {function} callback(translated) - Callback function giving back the translated C code.
 */
translate = function(callback){
	var i, j;
	var xml=fs.readFileSync("/home/mogyula/devel/dabox/test.xml", "utf8");
	var json = JSON.parse(parser.toJson(xml, {arrayNotation:true})); //Gotta get everything as array, so it'll be easier to walk the JSON tree.
	
	//TODO: While walking the xml, pay attention, that only given blocks can be embedded into each other (e.g. system-device-trigger()args-listener()args...)
	//TODO: Throw an error when a trigger was used instead of a listener and vice versa.
	//probably have to check the parent node.
	for (var i in json.system[0].device){
		for (var j in json.system[0].device[i].trigger){
			sortArgs(
				json.system[0].device[i].type,
				json.system[0].device[i].trigger[j].name,
				json.system[0].device[i].trigger[j].arg,
				i,j,null,null, //passing these, so the async callback function will get them
				function(trigger_arg_array, i, j){
					for (var k in json.system[0].device[i].trigger[j].device){
						for (var l in json.system[0].device[i].trigger[j].device[k].listener){
							sortArgs(
							json.system[0].device[i].trigger[j].device[k].type,
							json.system[0].device[i].trigger[j].device[k].listener[l].name,
							json.system[0].device[i].trigger[j].device[k].listener[l].arg,
							i,j,k,l,
							function(listener_arg_array, i, j, k, l){
								//here we can assemble the whole stuff
								var trig_com=json.system[0].device[i].id+"//"+
								json.system[0].device[i].type+"//"+
								json.system[0].device[i].trigger[j].name+"//"+
								trigger_arg_array.join("//")+"   "+
								json.system[0].device[i].trigger[j].device[k].id+"//"+
								json.system[0].device[i].trigger[j].device[k].type+"//"+
								json.system[0].device[i].trigger[j].device[k].listener[l].name+"//"+
								listener_arg_array.join("//");
								
								console.log(trig_com);
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
 * This function will sort the arguments givenen in the xml for triggers/listeners in a way, that the actual devices will be able to receive them in the right order at initialisation phase.
 * @param {string} device_type - The name of the device which trigger/listens to the function.
 * @param {string} func_name - The name of the trigger/listener function. 
 * @param {string[]} args - The arguments to short.
 * @param {function} callback(arg_array) - Callback function giving back the sorted argument string array.
 */
sortArgs = function(device_type, func_name, args, index_i, index_j, index_k, index_l, callback){
	var db = new sqlite3.Database("/home/mogyula/devel/dabox/id.db",sqlite3.OPEN_READONLY); //Open our database.
	
	if(!args){
		callback([""], index_i, index_j, index_k, index_l); //Return this if no arguments were given.
		return;
	}
	
	db.all("SELECT"+
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
		callback(_arg_array, index_i, index_j, index_k, index_l);
		return;
	});
	return;
}
	

