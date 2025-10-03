// Universal Live2D Expression Tester - works with any model
// Paste this entire script into your browser console

const panel = document.createElement('div');
panel.style.cssText = 'position:fixed; top:10px; right:10px; background:rgba(0,0,0,0.9); color:white; padding:15px; border-radius:8px; z-index:99999; font-family:monospace; font-size:12px; max-height:90vh; overflow-y:auto; width:280px;';

// Try to detect current model name
let modelName = 'Unknown';
if (window.live2dModel?._modelSetting?._modelHomeDir) {
  modelName = window.live2dModel._modelSetting._modelHomeDir.split('/').filter(x => x).pop() || 'Unknown';
}

panel.innerHTML = `<h3 style="margin:0 0 10px 0;">Live2D Expression Tester</h3><div style="font-size:10px; color:#90EE90; margin-bottom:10px;">Current Model: ${modelName}</div>`;

// Generate indices 0-15 (covers most models)
const indices = Array.from({length: 16}, (_, i) => i);

const resultDiv = document.createElement('div');
resultDiv.style.cssText = 'margin-top:10px; padding:10px; background:rgba(255,255,255,0.1); border-radius:4px; font-size:10px; max-height:200px; overflow-y:auto;';
resultDiv.innerHTML = '<strong>Click to test expressions:</strong><br>';
panel.appendChild(resultDiv);

indices.forEach((idx) => {
  const btn = document.createElement('button');
  btn.textContent = `Expression ${idx}`;
  btn.style.cssText = 'display:inline-block; width:48%; margin:2px 1%; padding:8px; cursor:pointer; background:#4a5568; color:white; border:none; border-radius:4px; font-size:10px;';
  btn.onclick = () => {
    if (window.live2dModel?.setExpression) {
      window.live2dModel.setExpression(idx);
    } else if (window.model?.setExpression) {
      window.model.setExpression(idx);
    } else {
      const models = Object.keys(window).filter(k => window[k]?.setExpression);
      if (models.length > 0) {
        window[models[0]].setExpression(idx);
      } else {
        resultDiv.innerHTML += `<br><span style="color:#ff6b6b;">❌ No model found!</span>`;
        return;
      }
    }
    console.log('✅ Set expression to index ' + idx);
    resultDiv.innerHTML = `<strong>Last tested:</strong> Index ${idx}<br><span style="color:#90EE90;">Describe what you see</span>` + resultDiv.innerHTML.split('<br>').slice(1).join('<br>');
  };
  panel.appendChild(btn);
});

const closeBtn = document.createElement('button');
closeBtn.textContent = '❌ Close Panel';
closeBtn.style.cssText = 'display:block; width:100%; margin-top:15px; padding:10px; cursor:pointer; background:#e53e3e; color:white; border:none; border-radius:4px;';
closeBtn.onclick = () => panel.remove();
panel.appendChild(closeBtn);

document.body.appendChild(panel);
console.log('✅ Universal Expression Test Panel created!');
