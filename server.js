var translator = require('./translator');

translator.translate(function(err, translated){
		if(err){
			console.log(err);
		}else{
			console.log(translated);
		}
	});
