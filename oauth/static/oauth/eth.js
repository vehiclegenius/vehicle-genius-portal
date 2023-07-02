const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
const callbackUrl = `${window.location.origin}/oauth/callback`;

document.getElementById('eth-login').onclick = onclick;

async function onclick() {
  if (!window.ethereum) {
    return alert(`Please install MetaMask to use this app!`);
  }

  if (!window.Web3) {
    return alert(`Problem loading web3 library!`);
  }

  try {
    const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
    const walletAddress = accounts[0];
    console.log(`Wallet address: ${walletAddress}`)
    const challenge = await generateChallenge(walletAddress);
    console.log(`Challenge: ${challenge}`);
    const signature = await signChallenge(walletAddress, challenge);
    console.log(`Signature: ${signature}`)
    const final = await submitChallenge(JSON.parse(challenge), signature);

    if (final.success) {
      window.location.href = '/';
    }
  } catch (e) {
    console.error(`Problem fulfilling challenge`, e);
  }
}

async function generateChallenge(walletAddress) {
  return fetch('/oauth/generate_challenge/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify({ wallet_address: walletAddress }),
  })
    .then(res => res.text());
}

async function signChallenge(walletAddress, challenge) {
  const msg = `0x${toHex(JSON.parse(challenge).challenge)}`;
  return window.ethereum.request({
    method: 'personal_sign',
    params: [msg, walletAddress],
  });
}

async function submitChallenge(challenge, signature) {
  const payload = {
    state: challenge.state,
    signature,
  };

  const res = await fetch('/oauth/submit_challenge/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify(payload),
  })
    .then(res => res.json());

  return res;
}

function toHex(str) {
  let hexString = '';
  for (let i = 0; i < str.length; i++) {
    const hex = str.charCodeAt(i).toString(16);
    hexString += ('00' + hex).slice(-2); // Ensure each character is represented by two hexadecimal digits
  }
  return hexString;
}
