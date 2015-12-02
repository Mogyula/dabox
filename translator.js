var parser = require("xml2json");
var fs = require("fs");
var sqlite3 = require("sqlite3").verbose();

/**
 * This function will translate the raw xml into blocks of C initialisation code that will be built into the actual target binary.
 */
translate = function(){
	
	var xml;
	xml=fs.readFileSync("/home/mogyula/devel/dabox/test.xml", "utf8");
	var json = JSON.parse(parser.toJson(xml, {arrayNotation:true})); //Gotta get everything as array, so it'll be easier to walk the JSON tree.
	//console.dir(json.xml.device.length);
	
	//TODO: While walking the xml, pay attention, that only given blocks can be embedded into each other (e.g. system-device-trigger()args-listener()args...)
	//probably have to check the parent node.
	for (var i in json.system[0].device){
		for (var j in json.system[0].device[i].trigger){
			if (json.system[0].device[i].trigger[j].arg){ //check if any trigger args have been given
				//if so, sort them
				//console.log(json.system[0].device[i].trigger[j].arg[0].$t);
				sortArgs(
					json.system[0].device[i].type,
					json.system[0].device[i].trigger[j].name,
					json.system[0].device[i].trigger[j].arg,
					function(arg_array){
						
						console.log(arg_array);
					}
				);
			}
			//if (!json.system.device[i].trigger[j].arg){
			//console.log("defined");
			//}
		}
	}
	
	//initialisation code
	//running code
	//
	
	/*db.serialize(function(){
		db.each("SELECT name FROM type_id", function(err, row){
			console.log(row.name);
		});
	});*/
};
module.exports.translate=translate; //So it can be accessed from other source files.

/**
 * This function will sort the arguments givenen in the xml for triggers/listeners in a way, that the actual devices will be able to receive them in the right order at initialisation phase.
 *@param {string} device_type - The name of the device which trigger/listens to the function.
 *@param {string} func_name - The name of the trigger/listener function. 
 *@param {string[]} args - The arguments to short.
 *@param {function} callback(arg_array) - Callback function giving back the sorted argument string array.
 */
sortArgs = function(device_type, func_name, args, callback){
	var db = new sqlite3.Database("/home/mogyula/devel/dabox/id.db",sqlite3.OPEN_READONLY); //Open our database.
	
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
		callback(_arg_array);	
	});	
}
	

