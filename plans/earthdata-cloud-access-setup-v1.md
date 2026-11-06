# Earthdata access for OSW current depth research

Add Earthdata credentials to OSW's GitHub Actions secrets so a future cloud run
can authenticate to NASA's ECCO service. Keep credential values in the secrets
interface; reply in chat only when setup is complete.

## Create or activate your Earthdata account

Sign in at [NASA Earthdata Login](https://urs.earthdata.nasa.gov/). If you need
an account, follow NASA's [registration and email activation steps](https://urs.earthdata.nasa.gov/documentation/for_users/how_to_register).

NASA services can require application authorization. Complete any consent on
NASA's site for the actual application shown by the service. NASA documents
preauthorization under **Applications**, **Authorized Apps**, and **Approve More
Applications**; use the application details presented by NASA rather than a
guessed application name. [NASA application authorization](https://urs.earthdata.nasa.gov/documentation/for_users/how_to_preauth_app)

## Add credentials to the OSW repository

In [giodl73-repo/OSW](https://github.com/giodl73-repo/OSW), open **Settings**,
then **Secrets and variables**, **Actions**, and the **Secrets** tab. Choose
**New repository secret**, enter the name and value, and select **Add secret**.
[GitHub instructions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets?tool=webui)

Choose one credential route supported by `earthaccess`:

- An existing Earthdata Login token: add `EARTHDATA_TOKEN`.
- Your Earthdata username and password: add both `EARTHDATA_USERNAME` and
  `EARTHDATA_PASSWORD`.

If a token is configured, `earthaccess` uses it before the username/password
pair.
[Environment authentication](https://earthaccess.readthedocs.io/en/latest/user/howto/authenticate-with-environment-variables/),
[login API and token precedence](https://earthaccess.readthedocs.io/en/latest/api/#login)

## Cloud authentication contract

A future bounded metadata job can map the chosen secrets into its environment:

```yaml
env:
  EARTHDATA_TOKEN: ${{ secrets.EARTHDATA_TOKEN }}
  EARTHDATA_USERNAME: ${{ secrets.EARTHDATA_USERNAME }}
  EARTHDATA_PASSWORD: ${{ secrets.EARTHDATA_PASSWORD }}
```

The documented Python authentication sequence is:

```python
import earthaccess

earthaccess.login(strategy="environment", persist=False)
session = earthaccess.get_requests_https_session()
```

The explicit environment strategy avoids an interactive prompt, and
`persist=False` avoids writing credentials into a netrc file. The session
supports authenticated HTTPS requests; the selected ECCO service still needs
an actual authenticated metadata check. [earthaccess API](https://earthaccess.readthedocs.io/en/latest/api/)

These examples are inactive documentation. This change installs no credential
consumer, performs no login, and requests no protected metadata or velocity
arrays.

## After configuration

Reply **Earthdata configured**, without credential values. The next cloud step
is a bounded metadata check, preserving the existing source access restrictions.
Real dimension order, levels, missing values, coordinates, protocol compatibility,
and response limits must be established before freezing a depth-measurement
operator and requesting velocity arrays. The existing subset guard has synthetic
DAP2 coverage; the advertised service entry is DAP4 metadata. Credential setup
alone does not resolve that compatibility question.
