#!/usr/bin/env node

if (!process.argv[2] || !process.argv[3] || !process.argv[4] || !process.argv[5]) {
	console.log("USAGE: command [username] [password] [ip] [cmd]")
	console.log("COMMANDS:")
	console.log("  status - roomba status info")
	console.log(" minstat - roomba status info with full output")
	console.log("   clean - start a clean cycle")
	console.log("   start - start a clean")
	console.log("    stop - stop a clean")
	console.log("   pause - pause clean")
	console.log("  resume - resume clean")
	console.log("    dock - return home")
	console.log(" schedon - reset schedule to start every day at 8am")
	console.log("schedoff - disable scheduled runs")
	process.exit();
}

const user = process.argv[2];
const pass = process.argv[3];
const ip = process.argv[4];
const cmd = process.argv[5];

var dorita980 = require('dorita980');
var myRobotViaLocal = new dorita980.Local(user, pass, ip);

myRobotViaLocal.on('connect', init);

function init () {
	if(cmd == 'status') {
		myRobotViaLocal.getStatus()
		.then((result) => {
			console.log(result)
			myRobotViaLocal.end()
		})
		.catch(console.log);
	} else if(cmd == 'minstat') {
		myRobotViaLocal.getMinStat()
		.then((result) => {
			console.log(result)
			myRobotViaLocal.end()
		})
		.catch(console.log);
	} else if(cmd == 'start') {
		myRobotViaLocal.start()
		.then(() => myRobotViaLocal.end())
		.catch(console.log);
	} else if(cmd == 'clean') {
		myRobotViaLocal.clean()
		.then(() => myRobotViaLocal.end())
		.catch(console.log);
	} else if(cmd == 'pause') {
		myRobotViaLocal.pause()
		.then(() => myRobotViaLocal.end())
		.catch(console.log);
	} else if(cmd == 'stop') {
		myRobotViaLocal.stop()
		.then(() => myRobotViaLocal.end())
		.catch(console.log);
	} else if(cmd == 'resume') {
		myRobotViaLocal.resume()
		.then(() => myRobotViaLocal.end())
		.catch(console.log);
	} else if(cmd == 'dock') {
		myRobotViaLocal.dock()
		.then(() => myRobotViaLocal.end())
		.catch(console.log);
	} else if(cmd == 'schedon') {
		var newWeek = {"cycle":["start","start","start","start","start","start","start"],"h":[8,8,8,8,8,8,8],"m":[0,0,0,0,0,0,0]}
		myRobotViaLocal.setWeek(newWeek)
		.then(() => myRobotViaLocal.end())
		.catch(console.log);
	} else if(cmd == 'schedoff') {
		var newWeek = {"cycle":["none","none","none","none","none","none","none"],"h":[8,8,8,8,8,8,8],"m":[0,0,0,0,0,0,0]}
		myRobotViaLocal.setWeek(newWeek)
		.then(() => myRobotViaLocal.end())
		.catch(console.log);
	} else {
		console.log('unknown command: '+cmd);
		myRobotViaLocal.end()
	}
}
