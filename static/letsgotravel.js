const bucketlist = document.querySelector('#bucketlist');
const bucketlistHeader = document.querySelector('#bucketlist-header');
let countryName = '';
let bucketlistName = '';

bucketlist.addEventListener('click', async function(evt) {
    if (evt.target.tagName === 'LI') {
        countryName = evt.target.innerText;
        bucketlistName = bucketlistHeader.innerText;

        if ((await validateUserAccess(bucketlistName)) == 200) {
            evt.target.classList.toggle('done');
            completeBucketlistCountry(evt.target.className);
        }
    }
});

async function completeBucketlistCountry(completed) {
    const resp = await axios.post(`/bucketlists/country/${countryName}/complete`, {
        bucketlist_name: bucketlistName,
        completed: completed
    });
    console.log(resp.data);
}

async function validateUserAccess(bucketlistName) {
    const resp = await axios.get(`/users/${bucketlistName}/validate`);
    return resp.data.status;
}