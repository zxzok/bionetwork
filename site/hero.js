(function(){var c=document.getElementById("hero-net");if(!c)return;var g=c.getContext("2d"),W=560,H=420,d=window.devicePixelRatio||1;c.width=W*d;c.height=H*d;g.scale(d,d);
var P=[[280,210],[300,190],[260,190]],E=[[0,1],[1,2],[0,2]],T=[0,1,1,2,0,2],V=[[0,0],[0,0],[0,0]];var reduce=matchMedia("(prefers-reduced-motion: reduce)").matches;
function css(n){return getComputedStyle(document.documentElement).getPropertyValue(n).trim()}
function add(){var ch={};var k=0;while(k<2){var u=T[Math.floor(Math.random()*T.length)];if(!ch[u]){ch[u]=1;k++}}var n=P.length,a=Object.keys(ch).map(Number);P.push([P[a[0]][0]+(Math.random()-.5)*40,P[a[0]][1]+(Math.random()-.5)*40]);V.push([0,0]);a.forEach(function(u){E.push([n,u]);T.push(n,u)})}
function step(){var n=P.length,k=34;for(var i=0;i<n;i++){var fx=(W/2-P[i][0])*0.004,fy=(H/2-P[i][1])*0.004;for(var j=0;j<n;j++){if(i===j)continue;var dx=P[i][0]-P[j][0],dy=P[i][1]-P[j][1],dd=dx*dx+dy*dy+0.1;if(dd<14400){fx+=dx/dd*k*6;fy+=dy/dd*k*6}}V[i][0]=(V[i][0]+fx)*0.6;V[i][1]=(V[i][1]+fy)*0.6}
E.forEach(function(e){var a=P[e[0]],b=P[e[1]],dx=b[0]-a[0],dy=b[1]-a[1],L=Math.sqrt(dx*dx+dy*dy)||1,f=(L-k)*0.02;V[e[0]][0]+=dx/L*f;V[e[0]][1]+=dy/L*f;V[e[1]][0]-=dx/L*f;V[e[1]][1]-=dy/L*f});
for(i=0;i<n;i++){P[i][0]=Math.max(12,Math.min(W-12,P[i][0]+V[i][0]));P[i][1]=Math.max(12,Math.min(H-12,P[i][1]+V[i][1]))}}
function draw(){var deg=new Array(P.length).fill(0);E.forEach(function(e){deg[e[0]]++;deg[e[1]]++});g.clearRect(0,0,W,H);g.strokeStyle=css("--line");g.lineWidth=1;E.forEach(function(e){g.beginPath();g.moveTo(P[e[0]][0],P[e[0]][1]);g.lineTo(P[e[1]][0],P[e[1]][1]);g.stroke()});
P.forEach(function(p,i){g.fillStyle=deg[i]>=10?css("--hub"):css("--accent");g.beginPath();g.arc(p[0],p[1],2.5+Math.sqrt(deg[i])*1.5,0,7);g.fill()})}
for(var s=0;s<(reduce?150:40);s++){add();for(var t=0;t<5;t++)step()}for(t=0;t<120;t++)step();draw();if(reduce)return;
var tick=0;(function loop(){if(P.length<170&&tick%14===0)add();step();draw();tick++;requestAnimationFrame(loop)})();})();
