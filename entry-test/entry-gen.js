/* Sterling entry test generator. Same code in, same questions out. Shared by the slides and the scorecard. */
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const GEN_POOLS = {
  physStretch:[
    {q:"A toy car's wheels spin on a smooth floor, but the car barely moves. Why? What would you change?", a:"Not enough grip (friction). Rubber tyres, a rougher surface, or more weight on the wheels."},
    {q:"You drop a cricket ball and a tennis ball from the same height at the same time. Which lands first, and why?", a:"About the same time. Gravity speeds both up equally. Air slows the light ball very slightly. Most kids say the heavy one."},
    {q:"Same motor, bigger wheels. Does the robot go faster or slower? What is the catch?", a:"Faster, because each turn covers more ground. The catch: it needs more force, so it may struggle to start or climb."}
  ],
  draw:[
    {q:"Draw a battery, a switch and a bulb, so the switch turns the bulb on.", look:"One closed loop through all three parts."},
    {q:"Draw one battery, one switch and two bulbs, so the switch turns both bulbs on together.", look:"The switch sits in the part of the loop both bulbs share."},
    {q:"Draw one battery, two bulbs and two switches, so each switch controls its own bulb.", look:"Two separate branches, each with its own switch and bulb."}
  ],
  circQ:[
    {q:"Two bulbs are in one loop, one after the other. One bulb breaks. What happens to the other one?", a:"It goes off too. The loop is broken, so no current flows."},
    {q:"Two bulbs are each in their own loop on the same battery. One bulb breaks. What happens to the other one?", a:"It stays on. Its own loop is still complete."},
    {q:"Your torch won't turn on. Name three things you would check.", a:"Battery dead or in backwards, the bulb, the switch, a loose wire or contact."}
  ],
  circStretch:[
    {q:"A motor spins one way. What happens if you swap its two wires?", a:"It spins the other way. The current flows backward through it."},
    {q:"You put the battery into a toy car backwards. What does the motor do?", a:"It spins the other way, so the car drives backward."},
    {q:"You connect an LED the wrong way round. What happens, and why?", a:"It doesn't light. An LED only lets current flow one way."}
  ]
};
function makeTest(code){
  const r = mulberry32((Number(code)||0) * 2654435761 >>> 0);
  const int = (lo,hi) => lo + Math.floor(r()*(hi-lo+1));
  const pick = a => a[Math.floor(r()*a.length)];
  const pl = (n,w) => `${n} ${w}${n===1?'':'s'}`;

  /* robot path */
  let d=0,x=0,y=0; const steps=[];
  const move=n=>{ if(d===0)y+=n; else if(d===1)x+=n; else if(d===2)y-=n; else x-=n; steps.push(`Forward ${n}`); };
  const turn=t=>{ d=(d+(t==='right'?1:3))%4; steps.push(`Turn ${t}`); };
  move(int(2,5)); turn(pick(['right','left'])); move(int(2,5)); turn(pick(['right','left'])); move(int(2,5));
  const last = pick(['right','left',null]); if(last) turn(last);
  const pos=[]; if(x) pos.push(`${pl(Math.abs(x),'step')} to the ${x>0?'right':'left'}`); if(y) pos.push(`${pl(Math.abs(y),'step')} ${y>0?'toward':'away from'} the screen`);
  const facing=['facing the screen','facing right','facing away from the screen','facing left'][d];
  const robot = { steps, ans: pos.length ? `${pos.join(' and ')} from the start, ${facing}.` : `Back at the start, ${facing}.` };

  /* number pattern */
  const fam = pick(['gaps','x2p1','squares','fib']);
  let seq, next, why, hint;
  if(fam==='gaps'){ const s=int(1,5),k=int(1,2); let g=int(1,4); seq=[s]; const gaps=[]; for(let i=0;i<4;i++){ seq.push(seq[seq.length-1]+g); gaps.push(g); g+=k; } next=seq[seq.length-1]+g; gaps.push(g); why=`The gaps grow by ${k} each time: ${gaps.join(', ')}.`; hint='Look at the gaps between the numbers.'; }
  else if(fam==='x2p1'){ const s=int(1,4); seq=[s,2*s,2*s+1,4*s+2,4*s+3]; next=8*s+6; why='Times 2, then add 1, over and over.'; hint='Each number becomes the next in one of two ways.'; }
  else if(fam==='squares'){ const c=int(0,3); seq=[1,4,9,16,25].map(v=>v+c); next=36+c; why = c ? `Square numbers (1×1, 2×2, 3×3 ...) plus ${c}.` : 'Square numbers: 1×1, 2×2, 3×3 ...'; hint='Look at the gaps between the numbers.'; }
  else { const a=int(1,3), b=a+int(1,2); seq=[a,b]; while(seq.length<5) seq.push(seq[seq.length-1]+seq[seq.length-2]); next=seq[3]+seq[4]; why='Each number is the two before it added together.'; hint='Look at the two numbers before each one.'; }
  const pattern = { seq, next, why, hint };

  /* gears */
  const t=pick([8,10,12]), ratio=pick([2,3,4]), big=t*ratio, k=int(1,3);
  const smallDrives = r() < 0.5;
  const gear = smallDrives ? {
    driver:'small', small:t, big, turns:ratio*k,
    setup:`A small gear with ${t} teeth turns a big gear with ${big} teeth. The small gear turns ${ratio*k} times.`,
    qs:['How many times does the big gear turn?','Which gear turns with more force?'],
    a:`${pl(k,'time')}. The big gear has more force.`, why:`${ratio*k} × ${t} = ${ratio*k*t} teeth pass, and ${ratio*k*t} ÷ ${big} = ${k}. The big gear turns slower but stronger. This is why the robot uses geared motors.`
  } : {
    driver:'big', small:t, big, turns:k,
    setup:`A big gear with ${big} teeth turns a small gear with ${t} teeth. The big gear turns ${pl(k,'time')}.`,
    qs:['How many times does the small gear turn?','Which gear spins faster?'],
    a:`${ratio*k} times. The small gear spins faster, with less force.`, why:`${k} × ${big} = ${k*big} teeth pass, and ${k*big} ÷ ${t} = ${ratio*k}.`
  };

  /* wheel distance */
  const dcm = pick([15,20,25,30,40,50]), n = int(3,6);
  const Ms = [1,2,3].filter(M => (M*100)%dcm===0), M = pick(Ms), tM = M*100/dcm;
  const wheel = { dcm, setup:`A robot wheel moves ${dcm} cm forward every time it turns once.`,
    qs:[`How far does the robot go in ${n} turns?`, `How many turns to go ${pl(M,'metre')}?`],
    a:`${dcm*n} cm. ${tM} turns.`, why:`${n} × ${dcm} = ${dcm*n} cm. ${M*100} ÷ ${dcm} = ${tM}.` };

  return { code:String(code), robot, pattern, gear, wheel,
    physStretch: pick(GEN_POOLS.physStretch), draw: pick(GEN_POOLS.draw),
    circQ: pick(GEN_POOLS.circQ), circStretch: pick(GEN_POOLS.circStretch) };
}
